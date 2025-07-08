import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Box, Typography, TextField, Button, IconButton,
  CircularProgress, Avatar, Paper, Grid
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
  const [chats, setChats] = useState([]);

  // Cargar el chat y la lista de chats al montar el componente
  useEffect(() => {
    fetchChat();
    fetchChats();
  }, [chatId]);

  // Scroll to bottom of chat when there are new messages
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
      console.error('Error loading chat:', err);
      setError('Could not load chat. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchChats = async () => {
    try {
      const response = await axios.get(`${API_URL}/chats`);
      setChats(response.data);
    } catch (err) {
      console.error('Error loading chats list:', err);
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
      console.error('Error sending message:', err);
      setError('Could not send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const handleBack = () => {
    navigate('/');
  };
  
  const handleCreateNewChat = async () => {
    try {
      const response = await axios.post(`${API_URL}/chats`, {
        title: 'New Chat'
      });
      navigate(`/chats/${response.data.id}`);
    } catch (err) {
      console.error('Error creating new chat:', err);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
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
          Chat not found
        </Typography>
      </Container>
    );
  }

  return (
    <Container>
      <Grid container spacing={4} sx={{ pt: 4 }}>
        {/* Sidebar */}
        <Grid item xs={12} md={3}>
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
              startIcon={<span>+</span>}
            >
              New Chat
            </Button>
            
            <Box sx={{ mt: 2 }}>
              {chats.map(c => (
                <Box 
                  key={c.id}
                  component="button"
                  onClick={() => navigate(`/chats/${c.id}`)}
                  sx={{ 
                    width: '100%',
                    p: 1.5, 
                    mb: 1, 
                    borderRadius: 1.5,
                    backgroundColor: c.id === chat.id ? 'rgba(25,118,210,0.1)' : 'transparent',
                    border: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: c.id === chat.id ? 'rgba(25,118,210,0.1)' : 'rgba(0,0,0,0.04)' },
                    display: 'block'
                  }}
                >
                  <Typography variant="body2" noWrap>{c.title}</Typography>
                </Box>
              ))}
            </Box>
          </Box>
        </Grid>
        
        {/* Main Content */}
        <Grid item xs={12} md={9}>
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
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <IconButton 
                  onClick={handleBack} 
                  sx={{ display: { xs: 'inline-flex', md: 'none' }, mr: 1 }}
                >
                  <ArrowBackIcon />
                </IconButton>
                <Typography variant="h6" component="h1" sx={{ fontWeight: 600 }}>
                  {chat.title}
                </Typography>
              </Box>
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
              {chat.messages.length === 0 ? (
                <Box sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%'
                }}>
                  <Typography variant="body1" color="text.secondary">
                    No messages yet. Start the conversation.
                  </Typography>
                </Box>
              ) : (
                chat.messages.map((msg, index) => (
                  <Box 
                    key={index}
                    sx={{ 
                      mb: 3
                    }}
                  >
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ mb: 1 }}
                    >
                      {msg.is_bot ? 'Window to Truth' : 'User'}
                    </Typography>
                    
                    <Box sx={{ 
                      maxWidth: '80%',
                      p: 2, 
                      borderRadius: 1,
                      ml: msg.is_bot ? 0 : 'auto',
                      mr: msg.is_bot ? 'auto' : 0,
                      bgcolor: msg.is_bot ? 'white' : '#1976d2',
                      color: msg.is_bot ? 'text.primary' : 'white',
                      boxShadow: msg.is_bot ? 1 : 'none'
                    }}>
                      {msg.is_bot ? (
                        <ReactMarkdown>
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        <Typography>{msg.content}</Typography>
                      )}
                    </Box>
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
                placeholder="Write your question..."
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
                      {sending ? <CircularProgress size={24} /> : 'Send'}
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
        </Grid>
      </Grid>
    </Container>
  );
};

export default ChatView;
