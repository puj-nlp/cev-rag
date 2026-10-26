import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import FormattedMessage, { toSafeHtml } from './FormattedMessage';

describe('FormattedMessage sanitization', () => {
  it('renders formatting but no injected elements from LLM output', () => {
    render(<FormattedMessage content={'Hola <img src=x alt="xss" onerror="alert(1)"> **mundo** [1]'} />);
    expect(screen.queryByRole('img')).toBeNull();
    expect(screen.getByText('mundo')).toBeInTheDocument();
    expect(screen.getByText('[1]')).toHaveClass('chat-reference');
  });

  it('strips scripts, event handlers and links', () => {
    expect(toSafeHtml('a<script>alert(2)</script>b')).toBe('ab');
    expect(toSafeHtml('<img src=x onerror="alert(1)">')).toBe('');
    expect(toSafeHtml('<span class="chat-reference" onclick="x()">[2]</span>')).toBe('<span class="chat-reference">[2]</span>');
    expect(toSafeHtml('<a href="javascript:alert(1)">x</a>')).toBe('x');
  });
});
