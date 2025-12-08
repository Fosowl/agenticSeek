
// Mock react-markdown to avoid ESM issues in Jest
jest.mock("react-markdown", () => (props) => {
  return <div data-testid="markdown">{props.children}</div>;
});

// Mock axios and other dependencies if necessary, but for now we focus on the import crash
// We also need to mock StandaloneBackend if it's used directly
jest.mock("./services/StandaloneBackend", () => ({
  get: jest.fn().mockResolvedValue({ data: {} }),
  post: jest.fn().mockResolvedValue({ data: {} }),
}));

import { render, screen } from '@testing-library/react';
import App from './App';

test('renders AgenticSeek header', () => {
  render(<App />);
  const headerElement = screen.getByText(/AgenticSeek/i);
  expect(headerElement).toBeInTheDocument();
});
