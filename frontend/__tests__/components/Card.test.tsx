/**
 * Tests for Card component
 */
import { render, screen } from '@testing-library/react'
import Card from '@/components/ui/Card'

describe('Card', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <h1>Test Heading</h1>
        <p>Test content</p>
      </Card>
    )

    expect(screen.getByText('Test Heading')).toBeInTheDocument()
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('applies default styling classes', () => {
    const { container } = render(<Card>Content</Card>)
    const cardDiv = container.firstChild

    expect(cardDiv).toHaveClass('bg-card')
    expect(cardDiv).toHaveClass('rounded-lg')
    expect(cardDiv).toHaveClass('border')
    expect(cardDiv).toHaveClass('border-primary-red/30')
  })

  it('applies custom className when provided', () => {
    const { container } = render(
      <Card className="custom-class">Content</Card>
    )
    const cardDiv = container.firstChild

    expect(cardDiv).toHaveClass('custom-class')
    expect(cardDiv).toHaveClass('bg-card') // Should keep default classes
  })

  it('has hover effects', () => {
    const { container } = render(<Card>Content</Card>)
    const cardDiv = container.firstChild

    expect(cardDiv).toHaveClass('hover:-translate-y-0.5')
    expect(cardDiv).toHaveClass('hover:border-primary-red/50')
  })

  it('has transition effects', () => {
    const { container } = render(<Card>Content</Card>)
    const cardDiv = container.firstChild

    expect(cardDiv).toHaveClass('transition-all')
    expect(cardDiv).toHaveClass('duration-200')
  })
})
