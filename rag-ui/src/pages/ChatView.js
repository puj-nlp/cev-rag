import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Box, Typography, TextField, Paper, IconButton,
  CircularProgress, Divider, Avatar, Card, CardContent
} from '@mui/material';
import { Send as SendIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatView = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Cargar el chat al montar el componente
  useEffect(() => {
    fetchChat();
  }, [chatId]);

  // Hacer scroll al final del chat cuando hay nuevos mensajes
  useEffect(() => {
    scrollToBottom();
  }, [chat?.messages]);

  const fetchChat = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/chats/${chatId}`);
      setChat(response.data);
      setError(null);
    } catch (err) {
      console.error('Error al cargar el chat:', err);
      setError('No se pudo cargar el chat. Por favor, inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    try {
      setSending(true);
      
      // Optimistic update
      setChat(prev => ({
        ...prev,
        messages: [
          ...prev.messages,
          {
            content: message,
            is_bot: false,
            timestamp: new Date().toISOString()
          }
        ]
      }));
      
      setMessage('');
      
      // Send the message to the API
      const response = await axios.post(`${API_URL}/chats/${chatId}/messages`, {
        question: message,
        chat_id: chatId
      });
      
      // Add the bot response to the chat
      setChat(prev => ({
        ...prev,
        messages: [
          ...prev.messages,
          response.data
        ]
      }));
      
    } catch (err) {
      console.error('Error al enviar el mensaje:', err);
      setError('No se pudo enviar el mensaje. Por favor, inténtalo de nuevo.');
    } finally {
      setSending(false);
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" sx={{ mt: 4 }}>
          {error}
        </Typography>
      </Container>
    );
  }

  if (!chat) {
    return (
      <Container>
        <Typography sx={{ mt: 4 }}>
          Chat no encontrado
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={handleBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" component="h1">
          {chat.title}
        </Typography>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      <Paper 
        elevation={3} 
        sx={{ 
          height: 'calc(100vh - 240px)', 
          display: 'flex',
          flexDirection: 'column',
          mb: 2,
          p: 2,
          overflow: 'hidden'
        }}
      >
        <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2 }}>
          {chat.messages.length === 0 ? (
            <Typography align="center" color="text.secondary" sx={{ mt: 4 }}>
              No hay mensajes. Envía uno para comenzar la conversación.
            </Typography>
          ) : (
            chat.messages.map((msg, index) => (
              <Box 
                key={index}
                sx={{ 
                  display: 'flex',
                  flexDirection: msg.is_bot ? 'row' : 'row-reverse',
                  mb: 2
                }}
              >
                <Avatar 
                  sx={{ 
                    bgcolor: msg.is_bot ? 'secondary.main' : 'primary.main',
                    mr: msg.is_bot ? 1 : 0,
                    ml: msg.is_bot ? 0 : 1
                  }}
                >
                  {msg.is_bot ? 'AI' : 'U'}
                </Avatar>
                <Card 
                  sx={{ 
                    maxWidth: '75%',
                    bgcolor: msg.is_bot ? 'grey.100' : 'primary.light',
                    color: msg.is_bot ? 'text.primary' : 'white'
                  }}
                >
                  <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                    {msg.is_bot ? (
                      <ReactMarkdown>
                        {msg.content}
                      </ReactMarkdown>
                    ) : (
                      <Typography>{msg.content}</Typography>
                    )}
                    <Typography variant="caption" color={msg.is_bot ? 'text.secondary' : 'rgba(255,255,255,0.7)'} sx={{ display: 'block', textAlign: 'right', mt: 0.5 }}>
                      {formatDate(msg.timestamp)}
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            ))
          )}
          <div ref={messagesEndRef} />
        </Box>
        
        <Divider />
        
        <Box 
          component="form" 
          onSubmit={handleSendMessage}
          sx={{ 
            display: 'flex',
            alignItems: 'center',
            mt: 2
          }}
        >
          <TextField
            fullWidth
            placeholder="Escribe tu pregunta..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={sending}
            variant="outlined"
            autoComplete="off"
            sx={{ mr: 1 }}
          />
          <IconButton 
            type="submit"
            color="primary"
            disabled={sending || !message.trim()}
            aria-label="enviar mensaje"
          >
            {sending ? <CircularProgress size={24} /> : <SendIcon />}
          </IconButton>
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatView;
