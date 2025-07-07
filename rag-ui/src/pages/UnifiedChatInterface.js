import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Box, Typography, TextField, Button, IconButton,
  CircularProgress, Paper, Grid, Avatar
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon
} from '@mui/icons-material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const UnifiedChatInterface = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  
  // Estados para la lista de chats
  const [chats, setChats] = useState([]);
  const [loadingChats, setLoadingChats] = useState(true);
  
  // Estados para el chat activo
  const [activeChat, setActiveChat] = useState(null);
  const [loadingChat, setLoadingChat] = useState(false);
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Cargar la lista de chats al montar el componente
  useEffect(() => {
    fetchChats();
  }, []);

  // Cargar chat específico cuando cambia el chatId
  useEffect(() => {
    if (chatId) {
      fetchChat(chatId);
    } else {
      setActiveChat(null);
    }
  }, [chatId]);

  // Hacer scroll al final del chat cuando hay nuevos mensajes
  useEffect(() => {
    if (activeChat?.messages) {
      scrollToBottom();
    }
  }, [activeChat?.messages]);

  const fetchChats = async () => {
    try {
      setLoadingChats(true);
      const response = await axios.get(`${API_URL}/chats`);
      setChats(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading chats:', err);
      setError('Could not load chats. Please try again.');
    } finally {
      setLoadingChats(false);
    }
  };

  const fetchChat = async (id) => {
    try {
      setLoadingChat(true);
      const response = await axios.get(`${API_URL}/chats/${id}`);
      setActiveChat(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading chat:', err);
      setError('Could not load chat. Please try again.');
      setActiveChat(null);
    } finally {
      setLoadingChat(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleCreateNewChat = async () => {
    try {
      const response = await axios.post(`${API_URL}/chats`, {
        title: 'New Chat'
      });
      
      const newChat = response.data;
      setChats([newChat, ...chats]);
      navigate(`/chats/${newChat.id}`);
    } catch (err) {
      console.error('Error creating new chat:', err);
      setError('Could not create chat. Please try again.');
    }
  };

  const handleSelectChat = (id) => {
    navigate(`/chats/${id}`);
  };

  const handleDeleteChat = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!window.confirm('¿Estás seguro de que quieres eliminar este chat?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/chats/${id}`);
      setChats(chats.filter(chat => chat.id !== id));
      
      // Si el chat eliminado es el activo, navegar al inicio
      if (chatId === id.toString()) {
        navigate('/');
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
      setError('Could not delete chat. Please try again.');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || !activeChat) return;
    
    try {
      setSending(true);
      
      // Optimistic update
      setActiveChat(prev => ({
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
      const response = await axios.post(`${API_URL}/chats/${activeChat.id}/messages`, {
        question: message,
        chat_id: activeChat.id
      });
      
      // Add the bot response to the chat
      setActiveChat(prev => ({
        ...prev,
        messages: [
          ...prev.messages,
          response.data
        ]
      }));
      
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Could not send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const handleStartNewChatFromWelcome = async () => {
    await handleCreateNewChat();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderSidebar = () => (
    <Box sx={{ backgroundColor: '#f9fafb', p: 2, borderRadius: 2, height: '80vh' }}>
      <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
        Chats
      </Typography>
      
      <Button 
        variant="outlined" 
        fullWidth 
        sx={{ 
          justifyContent: 'flex-start', 
          mb: 1.5,
          borderRadius: 2,
          py: 1.2
        }}
        onClick={handleCreateNewChat}
        startIcon={<AddIcon />}
      >
        Nuevo Chat
      </Button>
      
      <Box sx={{ mt: 2 }}>
        {loadingChats ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : chats.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
            No hay chats aún. Crea uno nuevo para empezar.
          </Typography>
        ) : (
          <Box sx={{ overflowY: 'auto', maxHeight: '60vh' }}>
            {chats.map(chat => (
              <Box 
                key={chat.id}
                onClick={() => handleSelectChat(chat.id)}
                sx={{ 
                  p: 1.5, 
                  mb: 1, 
                  borderRadius: 1.5,
                  backgroundColor: chatId === chat.id.toString() ? 'rgba(25,118,210,0.1)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  '&:hover': { 
                    backgroundColor: chatId === chat.id.toString() ? 'rgba(25,118,210,0.1)' : 'rgba(0,0,0,0.04)'
                  }
                }}
              >
                <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                  <Typography variant="body2" noWrap sx={{ maxWidth: 180 }}>
                    {chat.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(chat.created_at)}
                  </Typography>
                </Box>
                <IconButton
                  size="small"
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                  sx={{ 
                    opacity: 0.6, 
                    '&:hover': { opacity: 1, color: 'error.main' } 
                  }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );

  const renderWelcomeScreen = () => (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      alignItems: 'center',
      height: '70vh'
    }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 600 }}>
        ¡Bienvenido a Ventana a la Verdad!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, textAlign: 'center', mb: 4 }}>
        Explora testimonios de la Comisión de la Verdad de Colombia. Haz preguntas y obtén respuestas basadas en la información recopilada.
      </Typography>
      <Button 
        variant="contained" 
        startIcon={<AddIcon />}
        onClick={handleStartNewChatFromWelcome}
        sx={{ borderRadius: 2, px: 4, py: 1 }}
      >
        Iniciar Nuevo Chat
      </Button>
    </Box>
  );

  const renderChatInterface = () => {
    if (loadingChat) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
          <CircularProgress />
        </Box>
      );
    }

    if (!activeChat) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
          <Typography variant="body1" color="text.secondary">
            Chat no encontrado
          </Typography>
        </Box>
      );
    }

    return (
      <Box 
        sx={{ 
          display: 'flex',
          flexDirection: 'column',
          height: '80vh',
          position: 'relative'
        }}
      >
        {/* Chat Header */}
        <Box sx={{ mb: 2, px: 2 }}>
          <Typography variant="h6" component="h1" sx={{ fontWeight: 600 }}>
            {activeChat.title}
          </Typography>
        </Box>
        
        {/* Messages Area */}
        <Paper
          sx={{ 
            flexGrow: 1, 
            overflowY: 'auto', 
            mb: 2,
            p: 2,
            bgcolor: '#ffffff',
            borderRadius: 2,
            boxShadow: 'none'
          }}
        >
          {activeChat.messages.length === 0 ? (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%'
            }}>
              <Avatar 
                sx={{ 
                  bgcolor: '#1976d2', 
                  mb: 2,
                  width: 56,
                  height: 56
                }}
              >
                <BotIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="body1" color="text.secondary" textAlign="center">
                ¡Hola! Soy Ventana a la Verdad.<br />
                Pregúntame sobre los testimonios de la Comisión de la Verdad de Colombia.
              </Typography>
            </Box>
          ) : (
            activeChat.messages.map((msg, index) => (
              <Box 
                key={index}
                sx={{ 
                  mb: 3,
                  display: 'flex',
                  flexDirection: 'row',
                  alignItems: 'flex-start',
                  justifyContent: msg.is_bot ? 'flex-start' : 'flex-end'
                }}
              >
                {/* Avatar - Solo mostrar para mensajes del bot */}
                {msg.is_bot && (
                  <Avatar 
                    sx={{ 
                      bgcolor: '#1976d2', 
                      mr: 2, 
                      mt: 0.5,
                      width: 32,
                      height: 32
                    }}
                  >
                    <BotIcon sx={{ fontSize: 18 }} />
                  </Avatar>
                )}
                
                {/* Mensaje */}
                <Box sx={{ 
                  maxWidth: '80%',
                  p: 2, 
                  borderRadius: 2,
                  bgcolor: msg.is_bot ? '#f5f5f5' : '#1976d2',
                  color: msg.is_bot ? 'text.primary' : 'white',
                  boxShadow: msg.is_bot ? 1 : 'none',
                  order: msg.is_bot ? 2 : 1
                }}>
                  {msg.is_bot ? (
                    <ReactMarkdown>
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    <Typography>{msg.content}</Typography>
                  )}
                </Box>

                {/* Avatar del usuario - Solo mostrar para mensajes del usuario */}
                {!msg.is_bot && (
                  <Avatar 
                    sx={{ 
                      bgcolor: '#757575', 
                      ml: 2, 
                      mt: 0.5,
                      width: 32,
                      height: 32,
                      order: 2
                    }}
                  >
                    <PersonIcon sx={{ fontSize: 18 }} />
                  </Avatar>
                )}
              </Box>
            ))
          )}
          <div ref={messagesEndRef} />
        </Paper>
        
        {/* Input Area */}
        <Box 
          component="form" 
          onSubmit={handleSendMessage}
          sx={{ 
            p: 2,
            mt: 'auto'
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
            InputProps={{
              endAdornment: (
                <Button
                  variant="contained"
                  disabled={sending || !message.trim()}
                  type="submit"
                  sx={{ ml: 1, borderRadius: 1 }}
                >
                  {sending ? <CircularProgress size={24} /> : 'Enviar'}
                </Button>
              ),
              sx: { 
                pr: 1,
                borderRadius: 2
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2
              }
            }}
          />
        </Box>
      </Box>
    );
  };

  return (
    <Container>
      <Grid container spacing={4} sx={{ pt: 4 }}>
        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          {renderSidebar()}
        </Grid>
        
        {/* Main Content */}
        <Grid item xs={12} md={9}>
          {error && (
            <Box sx={{ mb: 2 }}>
              <Typography color="error">
                {error}
              </Typography>
            </Box>
          )}
          
          {chatId ? renderChatInterface() : renderWelcomeScreen()}
        </Grid>
      </Grid>
    </Container>
  );
};

export default UnifiedChatInterface;
