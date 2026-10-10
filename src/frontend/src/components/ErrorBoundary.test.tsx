import { render, screen, act, fireEvent } from '@testing-library/react';
import ErrorBoundary from './ErrorBoundary';
import { expect, test, vi, describe, beforeEach, afterEach, type MockInstance } from 'vitest';

const Thrower = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>Healthy Child</div>;
};

describe('ErrorBoundary', () => {
  let consoleErrorSpy: MockInstance;

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  test('renders children normally', () => {
    render(
      <ErrorBoundary>
        <Thrower shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Healthy Child')).toBeInTheDocument();
  });

  test('catches error and shows alert', () => {
    render(
      <ErrorBoundary>
        <Thrower shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('Something went wrong while showing this page.')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  test('Try again button clears the error state', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <Thrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByRole('alert')).toBeInTheDocument();
    
    // Rerender with healthy child
    rerender(
      <ErrorBoundary>
        <Thrower shouldThrow={false} />
      </ErrorBoundary>
    );
    
    const tryAgainBtn = screen.getByRole('button', { name: /Try again/i });
    act(() => {
      fireEvent.click(tryAgainBtn);
    });
    
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getByText('Healthy Child')).toBeInTheDocument();
  });

  test('changing resetKey clears the error state', () => {
    const { rerender } = render(
      <ErrorBoundary resetKey="a">
        <Thrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByRole('alert')).toBeInTheDocument();
    
    rerender(
      <ErrorBoundary resetKey="b">
        <Thrower shouldThrow={false} />
      </ErrorBoundary>
    );
    
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getByText('Healthy Child')).toBeInTheDocument();
  });
});
