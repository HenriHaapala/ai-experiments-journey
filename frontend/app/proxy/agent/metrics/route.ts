import { NextResponse } from 'next/server';

export async function GET() {
    try {
        // In Docker network, the agent service is accessible at http://agent:8001
        // Fallback to localhost if running outside docker (e.g. npm run dev)
        const agentUrl = process.env.AGENT_INTERNAL_URL || 'http://agent:8001';

        // Attempt to fetch from the agent service
        // Note: We use a short timeout to fail fast if agent is down
        const res = await fetch(`${agentUrl}/metrics`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            cache: 'no-store', // Don't cache real-time metrics
        });

        if (!res.ok) {
            return NextResponse.json(
                { error: `Agent service error: ${res.statusText}` },
                { status: res.status }
            );
        }

        const data = await res.json();
        return NextResponse.json(data);

    } catch (error) {
        console.error('Error proxying to agent service:', error);
        return NextResponse.json(
            { error: 'Failed to connect to agent service' },
            { status: 502 } // Bad Gateway
        );
    }
}
