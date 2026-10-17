import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import Chatbot from './Chatbot';
import { setupMockApi, restoreMockApi, recordedCalls, overrideMock } from '../../testing/mockApi';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

const ask = (q: string) => {
  fireEvent.change(screen.getByLabelText('Your question'), { target: { value: q } });
  fireEvent.click(screen.getByRole('button', { name: 'Send' }));
};

describe('Chatbot', () => {
  beforeEach(() => setupMockApi());
  afterEach(() => {
    cleanup();
    restoreMockApi();
  });

  test('send is disabled when blank and the input is limited to 1000 characters', () => {
    render(<Chatbot />);
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Your question'), { target: { value: '   ' } });
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();
    expect(screen.getByLabelText('Your question')).toHaveAttribute('maxlength', '1000');
  });

  test('request body is {worker_profile:{}, question}', async () => {
    render(<Chatbot />);
    ask('  How risky is my job?  ');
    await screen.findByText(/Please fill in the Worker Analysis page/);
    const post = recordedCalls.find((c) => c.url.endsWith('/chatbot/query'));
    expect(post?.body).toEqual({ worker_profile: {}, question: 'How risky is my job?' });
    expect(screen.getByText('How risky is my job?')).toBeInTheDocument();
  });

  test('assistant Markdown is rendered (bold -> strong)', async () => {
    overrideMock('POST /chatbot/query', { status: 200, body: { response: '**Worker Analysis** done' } });
    render(<Chatbot />);
    ask('hi');
    const strong = await screen.findByText('Worker Analysis');
    expect(strong.tagName).toBe('STRONG');
  });

  test('javascript: links are not anchors, https links are', async () => {
    overrideMock('POST /chatbot/query', {
      status: 200,
      body: { response: '[bad](javascript:alert(1)) and [good](https://example.org)' },
    });
    render(<Chatbot />);
    ask('links');
    const good = await screen.findByRole('link', { name: 'good' });
    expect(good).toHaveAttribute('href', 'https://example.org/');
    expect(good).toHaveAttribute('rel', 'noopener noreferrer');
    expect(screen.queryByRole('link', { name: 'bad' })).not.toBeInTheDocument();
    expect(screen.getByText('bad')).toBeInTheDocument();
  });

  test('raw HTML is neither executed nor rendered as an element', async () => {
    overrideMock('POST /chatbot/query', { status: 200, body: { response: 'before <script>window.__x=1</script> <b>bold</b> after' } });
    const { container } = render(<Chatbot />);
    ask('html');
    await screen.findByText(/before/);
    expect(container.querySelector('script')).toBeNull();
    expect(container.querySelector('b')).toBeNull();
    expect((window as unknown as Record<string, unknown>).__x).toBeUndefined();
  });

  test('failure shows "Error: ..." and re-enables sending', async () => {
    overrideMock('POST /chatbot/query', { status: 502, body: { detail: 'Chatbot failed: x' } });
    render(<Chatbot />);
    ask('boom');
    expect(await screen.findByText('Error: Chatbot failed: x')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Your question'), { target: { value: 'again' } });
    await waitFor(() => expect(screen.getByRole('button', { name: 'Send' })).toBeEnabled());
  });
});
