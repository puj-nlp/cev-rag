import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Box, Typography, TextField, Button, IconButton,
  CircularProgress, Paper, Grid, Avatar, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const UnifiedChatInterface = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  
  // Generate or retrieve unique session ID for this browser
  const getSessionId = () => {
    let sessionId = localStorage.getItem('ventana_session_id');
    if (!sessionId) {
      // Generate a unique ID using timestamp + random
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('ventana_session_id', sessionId);
    }
    return sessionId;
  };

  const sessionId = getSessionId();
  
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

  // Load specific chat when chatId changes
  useEffect(() => {
    if (chatId) {
      fetchChat(chatId);
    } else {
      setActiveChat(null);
    }
  }, [chatId]);

  // Scroll to bottom of chat when there are new messages
  useEffect(() => {
    if (activeChat?.messages) {
      scrollToBottom();
    }
  }, [activeChat?.messages]);

  const fetchChats = async () => {
    try {
      setLoadingChats(true);
      // Send sessionId as parameter to filter chats by session
      const response = await axios.get(`${API_URL}/chats?session_id=${sessionId}`);
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
        title: 'New Chat',
        session_id: sessionId  // Include session_id when creating the chat
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
    
    if (!window.confirm('Are you sure you want to delete this chat?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/chats/${id}`);
      setChats(chats.filter(chat => chat.id !== id));
      
      // If the deleted chat is the active one, navigate to home
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
      
      // Check if this is the first message (to update chat title in UI)
      const isFirstMessage = activeChat.messages.length === 0;
      const userMessage = message;
      
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
        ],
        // Update title locally if this is the first message
        title: isFirstMessage ? (userMessage.length > 50 ? userMessage.substring(0, 50) + "..." : userMessage) : prev.title
      }));
      
      // Update chat title in the chats list if this is the first message
      if (isFirstMessage) {
        const chatTitle = userMessage.length > 50 ? userMessage.substring(0, 50) + "..." : userMessage;
        setChats(prev => prev.map(chat => 
          chat.id === activeChat.id 
            ? { ...chat, title: chatTitle }
            : chat
        ));
      }
      
      setMessage('');
      
      // Send the message to the API
      const response = await axios.post(`${API_URL}/chats/${activeChat.id}/messages`, {
        question: userMessage,
        chat_id: activeChat.id,
        session_id: sessionId  // Include session_id in messages
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

  // Optional function to clear session (can be useful for testing or support)
  const clearSession = () => {
    localStorage.removeItem('ventana_session_id');
    setChats([]);
    setActiveChat(null);
    navigate('/');
    // Reload to generate new session
    window.location.reload();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
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
      
      {/* Session indicator (only visible in development) */}
      {process.env.NODE_ENV === 'development' && (
        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
          Session: {sessionId.slice(-8)}
        </Typography>
      )}
      
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
        New Chat
      </Button>
      
      <Box sx={{ mt: 2 }}>
        {loadingChats ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : chats.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
            No chats yet. Create a new one to get started.
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
        Welcome to Window to Truth!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, textAlign: 'center', mb: 4 }}>
        Explore testimonies from Colombia's Truth Commission. Ask questions and get answers based on the compiled information.
      </Typography>
      <Button 
        variant="contained" 
        startIcon={<AddIcon />}
        onClick={handleStartNewChatFromWelcome}
        sx={{ borderRadius: 2, px: 4, py: 1 }}
      >
        Start New Chat
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
            Chat not found
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
                Hello! I'm Window to Truth.<br />
                Ask me about the testimonies from Colombia's Truth Commission.
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
                {/* Avatar - Only show for bot messages */}
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
                
                {/* Message */}
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
                    <Box>
                      <ReactMarkdown
                        components={{                        h3: ({ children }) => {
                          if (children && children.toString().toLowerCase().includes('sources')) {
                            // Hide sources section completely
                            return null;
                          }
                          return <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>{children}</Typography>;
                        },
                          p: ({ children }) => {
                            const text = children?.toString() || '';
                            // Hide source citations and "Sources" text completely
                            if (text.includes('ISBN') && text.includes('CEV') || 
                                text.toLowerCase().includes('sources') ||
                                text.toLowerCase() === 'sources') {
                              return null;
                            }
                            return <Typography variant="body1" sx={{ mb: 1.5, lineHeight: 1.6 }}>{children}</Typography>;
                          },
                          ol: ({ children }) => (
                            <Box component="ol" sx={{ pl: 2, mb: 2 }}>
                              {children}
                            </Box>
                          ),
                          ul: ({ children }) => (
                            <Box component="ul" sx={{ pl: 2, mb: 2 }}>
                              {children}
                            </Box>
                          ),
                          li: ({ children }) => {
                            const text = children?.toString() || '';
                            // Hide source citations and "Sources" text in list items
                            if (text.includes('ISBN') && text.includes('CEV') || 
                                text.toLowerCase().includes('sources') ||
                                text.toLowerCase() === 'sources') {
                              return null;
                            }
                            return (
                              <Box component="li" sx={{ mb: 0.5 }}>
                                <Typography variant="body1">{children}</Typography>
                              </Box>
                            );
                          },
                          strong: ({ children }) => (
                            <Typography component="span" sx={{ fontWeight: 'bold' }}>
                              {children}
                            </Typography>
                          ),
                          em: ({ children }) => (
                            <Typography component="span" sx={{ fontStyle: 'italic' }}>
                              {children}
                            </Typography>
                          ),
                          references: ({ children }) => (
                            <Box sx={{ 
                              mt: 3,
                              p: 2,
                              bgcolor: '#f8f9fa',
                              borderRadius: 2,
                              border: '1px solid #e0e0e0'
                            }}>
                              <Typography 
                                variant="h6" 
                                sx={{ 
                                  mb: 2,
                                  fontWeight: 'bold',
                                  color: '#1976d2',
                                  display: 'flex',
                                  alignItems: 'center'
                                }}
                              >
                                📚 Referencias
                              </Typography>
                              <Box sx={{ pl: 1 }}>
                                {children}
                              </Box>
                            </Box>
                          )
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                      
                      {/* Render references if they exist */}
                      {msg.references && msg.references.length > 0 && (
                        <Accordion 
                          defaultExpanded={false}
                          sx={{ 
                            mt: 3,
                            boxShadow: 'none',
                            border: '1px solid #e0e0e0',
                            borderRadius: 2,
                            '&:before': {
                              display: 'none',
                            },
                            '& .MuiAccordionSummary-root': {
                              backgroundColor: '#f8f9fa',
                              borderRadius: '8px 8px 0 0',
                              minHeight: 48,
                              '&.Mui-expanded': {
                                minHeight: 48,
                                borderRadius: '8px 8px 0 0',
                              }
                            },
                            '& .MuiAccordionDetails-root': {
                              backgroundColor: '#f8f9fa',
                              borderRadius: '0 0 8px 8px',
                              pt: 0
                            }
                          }}
                        >
                          <AccordionSummary
                            expandIcon={<ExpandMoreIcon />}
                            aria-controls="references-content"
                            id="references-header"
                          >
                            <Typography 
                              variant="h6" 
                              sx={{ 
                                fontWeight: 'bold',
                                color: '#1976d2',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1
                              }}
                            >
                              📚 Referencias ({msg.references.length})
                            </Typography>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Box sx={{ pl: 1 }}>
                              {msg.references.map((ref, refIndex) => (
                                <Box 
                                  key={refIndex}
                                  sx={{ 
                                    mb: 2,
                                    p: 1.5,
                                    bgcolor: '#ffffff',
                                    borderLeft: '4px solid #1976d2',
                                    borderRadius: '0 4px 4px 0',
                                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                  }}
                                >
                                  <Typography 
                                    variant="body2" 
                                    sx={{ 
                                      fontWeight: 'bold',
                                      color: '#1976d2',
                                      mb: 0.5
                                    }}
                                  >
                                    [{ref.number}]
                                  </Typography>
                                  <Typography 
                                    variant="body2" 
                                    sx={{ 
                                      mb: 1,
                                      lineHeight: 1.5
                                    }}
                                  >
                                    {ref.title}
                                  </Typography>
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                                    {ref.source_id && (
                                      <Typography 
                                        variant="caption" 
                                        sx={{ 
                                          bgcolor: '#e3f2fd',
                                          color: '#1976d2',
                                          px: 1,
                                          py: 0.5,
                                          borderRadius: 1,
                                          fontWeight: 'medium'
                                        }}
                                      >
                                        {ref.source_id}
                                      </Typography>
                                    )}
                                    {ref.page && (
                                      <Typography 
                                        variant="caption" 
                                        sx={{ 
                                          bgcolor: '#f3e5f5',
                                          color: '#7b1fa2',
                                          px: 1,
                                          py: 0.5,
                                          borderRadius: 1,
                                          fontWeight: 'medium'
                                        }}
                                      >
                                        Pág. {ref.page}
                                      </Typography>
                                    )}
                                    {ref.year && (
                                      <Typography 
                                        variant="caption" 
                                        sx={{ 
                                          bgcolor: '#e8f5e8',
                                          color: '#2e7d32',
                                          px: 1,
                                          py: 0.5,
                                          borderRadius: 1,
                                          fontWeight: 'medium'
                                        }}
                                      >
                                        {ref.year}
                                      </Typography>
                                    )}
                                  </Box>
                                  {ref.url && (
                                    <Typography 
                                      component="a"
                                      href={ref.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      variant="caption"
                                      sx={{ 
                                        color: '#1976d2',
                                        textDecoration: 'none',
                                        '&:hover': {
                                          textDecoration: 'underline'
                                        }
                                      }}
                                    >
                                      🔗 Ver fuente completa
                                    </Typography>
                                  )}
                                </Box>
                              ))}
                            </Box>
                          </AccordionDetails>
                        </Accordion>
                      )}
                    </Box>
                  ) : (
                    <Typography>{msg.content}</Typography>
                  )}
                </Box>

                {/* User avatar - Only show for user messages */}
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
