/**
 * Renders assistant chat text as Markdown. Raw HTML is skipped and only
 * http(s) links become anchors; any other link is shown as plain text.
 */
import ReactMarkdown from 'react-markdown';
import { safeHttpUrl } from '../utils/workerData';

interface MarkdownMessageProps {
  text: string;
}

export default function MarkdownMessage({ text }: MarkdownMessageProps) {
  return (
    <div className="space-y-2 break-words">
      <ReactMarkdown
        skipHtml
        components={{
          a: ({ href, children }) => {
            const safe = safeHttpUrl(href);
            if (safe === null) return <span>{children}</span>;
            return (
              <a href={safe} target="_blank" rel="noopener noreferrer" className="text-accent underline">
                {children}
              </a>
            );
          },
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}
