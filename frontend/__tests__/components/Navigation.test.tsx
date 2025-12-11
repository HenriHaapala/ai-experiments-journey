/**
 * Tests for Navigation component
 */
import { render, screen } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import Navigation from '@/components/layout/Navigation'

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('Navigation', () => {
  beforeEach(() => {
    ;(usePathname as jest.Mock).mockReturnValue('/')
  })

  it('renders the site title', () => {
    render(<Navigation />)
    const title = screen.getByText('HENRI HAAPALA')
    expect(title).toBeInTheDocument()
  })

  it('renders all navigation links', () => {
    render(<Navigation />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Roadmap')).toBeInTheDocument()
    expect(screen.getByText('MCP Learning Log')).toBeInTheDocument()
  })

  it('highlights the active page', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/roadmap')
    render(<Navigation />)

    const roadmapLink = screen.getByText('Roadmap')
    expect(roadmapLink).toHaveClass('text-primary-red')
  })

  it('does not highlight inactive pages', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/roadmap')
    render(<Navigation />)

    const homeLink = screen.getByText('Home')
    expect(homeLink).not.toHaveClass('text-primary-red')
    expect(homeLink).toHaveClass('text-text-light')
  })

  it('has correct href attributes', () => {
    render(<Navigation />)

    const homeLink = screen.getByText('Home').closest('a')
    const roadmapLink = screen.getByText('Roadmap').closest('a')
    const learningLink = screen.getByText('MCP Learning Log').closest('a')

    expect(homeLink).toHaveAttribute('href', '/')
    expect(roadmapLink).toHaveAttribute('href', '/roadmap')
    expect(learningLink).toHaveAttribute('href', '/learning')
  })

  it('renders as a sticky navigation bar', () => {
    const { container } = render(<Navigation />)
    const nav = container.querySelector('nav')

    expect(nav).toHaveClass('sticky')
    expect(nav).toHaveClass('top-0')
  })
})
