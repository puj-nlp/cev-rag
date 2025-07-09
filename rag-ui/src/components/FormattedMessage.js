import React from 'react';
import { Typography, Box } from '@mui/material';

const FormattedMessage = ({ content, isUser = false }) => {
  // Función para procesar el texto y dividirlo en párrafos
  const formatContent = (text) => {
    if (!text) return [];
    
    // Dividir por párrafos y limpiar
    const paragraphs = text
      .split(/\n\s*\n/)
      .filter(p => p.trim().length > 0)
      .map(p => p.trim());
    
    return paragraphs;
  };

  // Función para procesar referencias [1], [2], etc.
  const processReferences = (text) => {
    return text.replace(/\[(\d+)\]/g, (match, num) => {
      return `<span class="chat-reference">[${num}]</span>`;
    });
  };

  // Función para procesar texto con negritas y cursivas
  const processMarkdown = (text) => {
    // Procesar negritas **texto**
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Procesar cursivas *texto*
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Procesar referencias
    text = processReferences(text);
    return text;
  };

  const paragraphs = formatContent(content);

  return (
    <Box
      className="chat-message"
      sx={{
        backgroundColor: isUser ? '#f5f5f5' : '#ffffff',
        padding: '20px',
        borderRadius: '12px',
        marginBottom: '16px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        maxWidth: '800px',
        margin: '0 auto 16px auto',
        border: isUser ? '1px solid #e0e0e0' : 'none',
      }}
    >
      {paragraphs.map((paragraph, index) => (
        <Typography
          key={index}
          variant="body1"
          sx={{
            marginBottom: index < paragraphs.length - 1 ? '16px' : '0',
            textAlign: 'justify',
            textJustify: 'inter-word',
            lineHeight: 1.8,
            fontSize: '16px',
            fontWeight: 400,
            color: '#2c2c2c',
            fontFamily: 'Cinzel, serif',
            '& .chat-reference': {
              backgroundColor: '#e3f2fd',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '14px',
              fontWeight: 500,
              color: '#1976d2',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: '#bbdefb',
              }
            },
            '& strong': {
              fontWeight: 600,
            },
            '& em': {
              fontStyle: 'italic',
            }
          }}
          dangerouslySetInnerHTML={{
            __html: processMarkdown(paragraph)
          }}
        />
      ))}
    </Box>
  );
};

export default FormattedMessage;
