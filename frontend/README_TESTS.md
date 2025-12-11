# Frontend Testing Guide

## Test Files Created

✅ **Test Infrastructure Complete:**
- `jest.config.js` - Jest configuration with Next.js integration
- `jest.setup.js` - Test environment setup
- `__tests__/components/Navigation.test.tsx` - Navigation component tests (6 tests)
- `__tests__/components/Card.test.tsx` - Card component tests (5 tests)

## Running Tests

### Option 1: Local Development (Recommended)

**Install test dependencies:**
```bash
cd frontend
npm install
```

**Run all tests:**
```bash
npm test
```

**Run tests in watch mode (during development):**
```bash
npm run test:watch
```

**Run with coverage:**
```bash
npm run test:coverage
```

### Option 2: Docker

**Rebuild frontend image with test dependencies:**
```bash
docker-compose build frontend
docker-compose up -d frontend
```

**Run tests in Docker:**
```bash
docker-compose exec frontend npm test
```

**Run with coverage in Docker:**
```bash
docker-compose exec frontend npm run test:coverage
```

## Test Coverage

### Component Tests

#### Navigation Component (`Navigation.test.tsx`)
- ✅ Renders site title "HENRI HAAPALA"
- ✅ Renders all navigation links (Home, Roadmap, Learning Log)
- ✅ Highlights active page based on current route
- ✅ Does not highlight inactive pages
- ✅ Has correct href attributes for all links
- ✅ Renders as sticky navigation bar with correct classes

#### Card Component (`Card.test.tsx`)
- ✅ Renders children correctly
- ✅ Applies default styling classes (bg-card, rounded-lg, border)
- ✅ Applies custom className when provided
- ✅ Has hover effects (translate-y, border color change)
- ✅ Has transition effects (transition-all, duration-200)

## Test Framework Stack

- **Jest 29** - Test runner and assertion library
- **React Testing Library 16** - Component testing utilities
- **@testing-library/jest-dom** - Custom Jest matchers for DOM
- **jest-environment-jsdom** - DOM environment for browser tests
- **Next.js Jest Config** - Automatic Next.js configuration

## Writing New Tests

### Example: Testing a Component

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MyComponent from '@/components/MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('handles user interaction', async () => {
    const user = userEvent.setup()
    render(<MyComponent />)

    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)

    expect(screen.getByText('Clicked!')).toBeInTheDocument()
  })
})
```

### Mocking Next.js Features

```tsx
// Mock useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: '/',
  }),
  usePathname: jest.fn(() => '/'),
}))

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }) => <a href={href}>{children}</a>
})
```

## CI/CD Integration

Add to GitHub Actions workflow:

```yaml
frontend-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    - name: Run tests
      run: |
        cd frontend
        npm run test:coverage
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        files: ./frontend/coverage/coverage-final.json
```

## Test Execution Time

Current tests run in < 2 seconds (fast unit tests, no network calls).

## Coverage Goals

| Component Type | Target | Status |
|----------------|--------|--------|
| UI Components | 80% | ✅ 11 tests |
| Layouts | 70% | ✅ 6 tests |
| Pages | 60% | 🔲 TODO |
| Utilities | 90% | 🔲 TODO |

## Next Steps

1. ✅ Core component tests (Navigation, Card)
2. 🔲 Page component tests (Homepage, Roadmap, Learning)
3. 🔲 API client tests (fetch utilities)
4. 🔲 Hook tests (custom React hooks if any)
5. 🔲 Integration tests with MSW (Mock Service Worker)
6. 🔲 E2E tests with Playwright

## Troubleshooting

### Jest module resolution errors
If you see errors like "Cannot find module '@/components/...'":
- Check `jest.config.js` moduleNameMapper
- Ensure paths match your actual directory structure

### Next.js configuration issues
- The `next/jest` helper automatically handles Next.js config
- Make sure you're using `createJestConfig` as shown in jest.config.js

### CSS/Tailwind errors in tests
- Jest ignores CSS by default with Next.js config
- If needed, add CSS mocks in jest.setup.js

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Next.js Testing Guide](https://nextjs.org/docs/testing)
