from django.db.models import F
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from pgvector.django import CosineDistance

import os
import cohere
from groq import Groq

from .models import RoadmapSection, LearningEntry, KnowledgeChunk, RoadmapItem
from django.db.models import Q # Added for keyword search
from .serializers import RoadmapSectionSerializer, LearningEntrySerializer
from .utils.utils import smart_retrieve

class RoadmapSectionListView(generics.ListAPIView):
    queryset = RoadmapSection.objects.all().prefetch_related("items")
    serializer_class = RoadmapSectionSerializer


class PublicLearningEntryListView(generics.ListAPIView):
    queryset = (
        LearningEntry.objects.filter(is_public=True)
        .select_related("roadmap_item", "roadmap_item__section")
        .prefetch_related("media")
    )
    serializer_class = LearningEntrySerializer


class RoadmapProgressView(APIView):
    """
    GET /api/roadmap/progress/
    Returns progress statistics for the roadmap
    """
    def get(self, request, *args, **kwargs):
        sections = RoadmapSection.objects.all()
        items = RoadmapItem.objects.all()
        active_items = items.filter(is_active=True)
        items_with_entries = items.filter(learning_entries__isnull=False).distinct()

        learning_entries = LearningEntry.objects.all()
        knowledge_chunks = KnowledgeChunk.objects.all()

        # Calculate completion percentage
        total_items = items.count()
        completed_items = items_with_entries.count()
        completion_percentage = round((completed_items / total_items * 100), 1) if total_items > 0 else 0.0

        # Count chunks by source type
        chunks_by_source = {}
        for source_type in ['learning_entry', 'roadmap_item', 'site_content', 'document']:
            chunks_by_source[source_type] = knowledge_chunks.filter(source_type=source_type).count()

        return Response({
            "success": True,
            "stats": {
                "roadmap": {
                    "total_sections": sections.count(),
                    "total_items": total_items,
                    "active_items": active_items.count(),
                    "items_with_entries": completed_items,
                    "completion_percentage": completion_percentage
                },
                "learning": {
                    "total_entries": learning_entries.count(),
                    "public_entries": learning_entries.filter(is_public=True).count(),
                    "private_entries": learning_entries.filter(is_public=False).count()
                },
                "knowledge_base": {
                    "total_chunks": knowledge_chunks.count(),
                    "by_source": chunks_by_source
                }
            }
        })


class RAGSearchView(APIView):
    """
    POST /api/rag/search/
    Body: { "query": "...", "top_k": 5 }
    Performs semantic search using RAG
    """
    def post(self, request, *args, **kwargs):
        query = request.data.get("query", "").strip()
        top_k = request.data.get("top_k", 5)

        if not query:
            return Response(
                {"success": False, "error": "Missing 'query' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Setup Cohere client
        cohere_api_key = os.getenv("COHERE_API_KEY")
        cohere_model = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")

        if not cohere_api_key:
            return Response(
                {"success": False, "error": "Cohere API key not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        co_client = cohere.Client(cohere_api_key)

        # Generate embedding for query
        try:
            embed_resp = co_client.embed(
                texts=[query],
                model=cohere_model,
                input_type="search_query"
            )
            query_vector = embed_resp.embeddings[0]
        except Exception as e:
            return Response(
                {"success": False, "error": f"Failed to embed query: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Perform vector search
        try:
            chunks_qs, debug = smart_retrieve(
                query_vector,
                top_k=top_k,
                candidate_k=max(16, top_k * 3)
            )

            results = []
            for chunk in chunks_qs:
                results.append({
                    "id": chunk.id,
                    "source_type": chunk.source_type,
                    "title": chunk.title,
                    "content": chunk.content,
                    "section_title": chunk.section_title,
                    "item_title": chunk.item_title,
                    "tags": chunk.tags,
                    "similarity": getattr(chunk, 'similarity', None)
                })

            return Response({
                "success": True,
                "query": query,
                "top_k": top_k,
                "results": results,
                "debug": debug
            })

        except Exception as e:
            return Response(
                {"success": False, "error": f"Search failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningEntryListCreateView(generics.ListCreateAPIView):
    """
    GET /api/roadmap/learning-entries/ - List learning entries
    POST /api/roadmap/learning-entries/ - Create learning entry
    """
    serializer_class = LearningEntrySerializer

    def get_queryset(self):
        queryset = LearningEntry.objects.all().select_related(
            "roadmap_item", "roadmap_item__section"
        ).prefetch_related("media")

        # Filter by roadmap_item if provided
        roadmap_item_id = self.request.query_params.get('roadmap_item')
        if roadmap_item_id:
            queryset = queryset.filter(roadmap_item_id=roadmap_item_id)

        # Limit results if requested
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "entry": serializer.data
        }, status=status.HTTP_201_CREATED)

class AIChatView(APIView):
    """
    POST /api/ai/chat/
    Body: { "question": "..." }

    Uses Cohere to embed the question, pgvector to find similar LearningEntry
    embeddings, and Groq (Llama 3) to generate an answer based on your own notes.
    """

    def post(self, request, *args, **kwargs):
        question = request.data.get("question", "").strip()
        if not question:
            return Response(
                {"error": "Missing 'question' field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------------
        # SECURITY: Call Agent Service Guardrails
        # ---------------------------------------------------------------
        try:
            import requests
            # Use docker service name 'agent' and port 8001
            agent_url = os.getenv("AGENT_URL", "http://agent:8001")
            
            # 1. Validate Input
            validation_resp = requests.post(
                f"{agent_url}/api/validate", 
                json={"text": question},
                timeout=3
            )
            
            if validation_resp.status_code == 200:
                val_data = validation_resp.json()
                if not val_data.get("is_safe", True):
                    # Blocking Unsafe Content
                    reason = val_data.get("reason", "Security Violation")
                    return Response(
                        {
                            "answer": f"**SECURITY ALERT**: Request blocked. {reason}",
                            "question": question,
                            "context_used": [],
                            "confidence": 0.0,
                            "retrieval_debug": {"status": "blocked"},
                            "follow_up_questions": []
                        },
                        status=status.HTTP_200_OK
                    )
        except Exception as e:
            # Simple fail-open or log
            print(f"Warning: Agent guardrail check failed: {e}")
            pass
        # ---------------------------------------------------------------

        # Setup clients
        cohere_api_key = os.getenv("COHERE_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        groq_model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        cohere_model = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")

        if not cohere_api_key or not groq_api_key:
            return Response(
                {"error": "API keys not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        co_client = cohere.Client(cohere_api_key)
        groq_client = Groq(api_key=groq_api_key)

        rate_limited = False
        query_vector = None
        debug = {"status": "unknown"}
        chunks_qs = []
        low_conf = False
        fallback_active = False # Flag to indicate if we used SQL fallback
        fallback_context_str = ""

        # 1) Embed the question with Cohere
        try:
            embed_resp = co_client.embed(
                texts=[question],
                model=cohere_model,
                input_type="search_query",
            )
            query_vector = embed_resp.embeddings[0]
        except Exception as e:
            # Handle Cohere Rate Limit (429) gracefully
            print(f"Cohere API Error (likely Rate Limit): {e}. Switching to SQL Fallback.")
            rate_limited = True
            query_vector = None
            debug = {"status": "rate_limit_fallback"}

        # 2) Retrieval (Vector vs SQL Fallback)
        if query_vector is not None:
            # Normal Vector Search
            try:
                chunks_qs, debug = smart_retrieve(
                    query_vector,
                    top_k=5,
                    candidate_k=16,
                )

                if debug["status"] == "no_results":
                     low_conf = True 
                else:
                     low_conf = debug["status"] in ("low_confidence", "very_low_confidence")
            except Exception as e:
                print(f"PGVector failed: {e}. Fallback.")
                rate_limited = True # Treat DB error as need for fallback
        
        # ------------------------------------------------------------------
        # HYBRID RETRIEVAL: Trigger SQL Fallback if Rate Limited OR Low Confidence
        # ------------------------------------------------------------------
        if rate_limited or low_conf:
            fallback_active = True
            try:
                # A) Roadmap Summary (Always useful context)
                roadmap_items = RoadmapItem.objects.filter(is_active=True).select_related('section')
                sections = {}
                for item in roadmap_items:
                    sec = item.section.title if item.section else "General"
                    if sec not in sections: sections[sec] = []
                    sections[sec].append(f"{item.title} ({item.status})")
                
                fallback_context_str = "Roadmap Status (Active Items):\n"
                for sec, items in sections.items():
                    fallback_context_str += f"## {sec}\n" + "\n".join([f"- {i}" for i in items]) + "\n"

                # B) Dynamic Document Keyword Search (The Fix for 'React' missing in Vector DB)
                # We need to be careful not to filter out important words like 'years', 'experience'
                stop_words = {"does", "know", "henri", "what", "how", "is", "where", "when", "why", "who", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "about", "me", "you", "he", "she", "it", "document", "file", "pdfs"}
                
                # Extract keywords, keeping numbers and longer words
                keywords = [w.strip("?.!,") for w in question.split() if w.lower().strip("?.!,") not in stop_words and len(w) > 1]
                
                if keywords:
                    q_obj = Q()
                    for k in keywords:
                        q_obj |= Q(content__icontains=k) | Q(title__icontains=k)
                    
                    # Fetch MORE chunks to ensure we catch the 'Profile' section
                    doc_chunks = KnowledgeChunk.objects.filter(q_obj).order_by('-id')[:10]
                    
                    if doc_chunks.exists():
                        # KEY CHANGE: If we found direct keyword matches, we have HIGH confidence data.
                        # Disable "Low Confidence" mode so the LLM doesn't hedge or act weird.
                        low_conf = False 
                        fallback_context_str += "\n\n**Keyword-Matched Documents (Hybrid Search):**\n"
                        for i, c in enumerate(doc_chunks, 1):
                            fallback_context_str += f"[Doc {i} {c.title}]: {c.content[:600]}...\n\n"

            except Exception as e:
                print(f"Fallback construction failed: {e}")
                if not fallback_context_str:
                    fallback_context_str = "No specific data available."

        # 3) Context Assembly
        context_text = ""
        # Add Vector Chunks first
        parts = []
        if chunks_qs:
             for i, chunk in enumerate(chunks_qs, 1):
                 parts.append(f"[Vector Chunk {i}] {chunk.title}\n{chunk.content}")
        
        vector_context = "\n\n".join(parts) if parts else ""
        
        # Combine contexts
        full_context = ""
        if vector_context:
            full_context += f"### Vector Search Results:\n{vector_context}\n\n"
        if fallback_active and fallback_context_str:
            full_context += f"### Additional Context (Roadmap/Keywords):\n{fallback_context_str}\n\n"
        
        if not full_context:
            full_context = "No information found in Roadmap or Documents."

        
        # 4) System Prompt
        system_prompt = (
            "You are an AI assistant for Henri Haapala's portfolio.\n"
            "Rules:\n1) Answer based on context.\n2) If unknown, say 'I don't have enough info'.\n"
        )
        
        if rate_limited:
            system_prompt += (
                "\n**NOTICE**: Vector search is unavailable (Rate Limit). "
                "You are relying on Roadmap and Keyword Search data only."
            )
        elif low_conf:
             system_prompt += (
                "\n**NOTICE**: Vector search yielded low confidence. "
                "Supplementary Keyword Search data has been provided."
            )

        user_prompt = f"Question: {question}\n\nContext:\n{full_context}"

        # 5) Call Groq
        try:
            chat_resp = groq_client.chat.completions.create(
                model=groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            answer = chat_resp.choices[0].message.content
        except Exception as e:
             return Response({"error": str(e)}, status=500)

        # Generate follow-ups (simplified)
        follow_up_questions = []
        if not rate_limited:
             follow_up_questions = self._generate_follow_up_questions(question, [], groq_client, groq_model)

        return Response(
            {
                "answer": answer,
                "question": question,
                "context_used": [], # Simplified for now
                "confidence": 0.5 if not low_conf else 0.3, # Adjust score logic
                "retrieval_debug": debug,
                "follow_up_questions": follow_up_questions,
            },
            status=status.HTTP_200_OK,
        )

    def _generate_follow_up_questions(self, question, context_blocks, groq_client, groq_model):
        """
        Generate 3 context-aware follow-up questions to help the user refine their query.
        """
        if not context_blocks:
            # No context available - ask generic clarifying questions
            return [
                "What specific information about Henri are you looking for?",
                "Tell me more about what aspect of this topic interests you",
                "What would you like to know about Henri's work or experience?"
            ]

        # Build a summary of available topics from context
        topics = []
        for block in context_blocks[:3]:  # Use top 3 chunks
            if block.get('title'):
                topics.append(block['title'])
            if block.get('section_title'):
                topics.append(block['section_title'])
            if block.get('roadmap_item_title'):
                topics.append(block['roadmap_item_title'])

        # Remove duplicates while preserving order
        unique_topics = []
        seen = set()
        for topic in topics:
            if topic and topic not in seen:
                unique_topics.append(topic)
                seen.add(topic)

        topics_str = ", ".join(unique_topics[:5]) if unique_topics else "various topics"

        # Create a prompt to generate contextual follow-up questions
        followup_prompt = f"""Based on this user question: "{question}"

And these available topics in the knowledge base: {topics_str}

Generate exactly 3 helpful follow-up questions that the user could ask to refine their query and get better results.

Guidelines:
- Write questions from the USER'S perspective (first person: "What did Henri study...", "Tell me about...", etc.)
- Make questions specific to the available topics
- Ask about different aspects (implementation vs theory, specific tools, use cases, etc.)
- Keep questions concise (one sentence each)
- Make them natural and conversational
- DO NOT use second person ("Are you looking for...") - use first person or direct questions instead

Examples of good phrasing:
- "What technologies did Henri learn during his studies?"
- "Tell me more about Henri's education background"
- "What degree did Henri earn?"

Return ONLY the 3 questions, one per line, without numbering or bullet points."""

        try:
            response = groq_client.chat.completions.create(
                model=groq_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates clarifying follow-up questions."},
                    {"role": "user", "content": followup_prompt}
                ],
                temperature=0.7,  # Slightly more creative for question variety
                max_tokens=200,
            )

            # Parse the response - split by newlines and clean up
            questions_text = response.choices[0].message.content.strip()
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]

            # Remove any numbering or bullet points
            cleaned_questions = []
            for q in questions:
                # Remove common prefixes like "1.", "-", "*", etc.
                q = q.lstrip('0123456789.-*• ')
                if q and len(q) > 10:  # Sanity check
                    cleaned_questions.append(q)

            # Return up to 3 questions
            return cleaned_questions[:3] if cleaned_questions else []

        except Exception as e:
            # Fallback to generic questions if generation fails
            print(f"Failed to generate follow-up questions: {e}")
            return [
                f"What specifically about {unique_topics[0] if unique_topics else 'this topic'} would you like to know?",
                "Tell me more about the implementation details",
                "What other aspects of Henri's work interest you?"
            ]
