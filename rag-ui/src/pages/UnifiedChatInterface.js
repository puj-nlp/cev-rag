import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Box, Typography, TextField, Button, IconButton,
  CircularProgress, Paper, Avatar, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { 
  Person as PersonIcon,
  SmartToy as BotIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { apiService } from '../services/api';
import WindowContainer from '../components/WindowContainer';
import Sidebar from '../components/Sidebar';
import WelcomeScreen from '../components/WelcomeScreen';

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
  
  // Estado para colapsar/expandir sidebar - por defecto cerrado
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);
  
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
      const response = await apiService.getChats(sessionId);
      setChats(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading chats:', err);
      setError('Could not load chats. There is currently high user traffic, please try again later.');
    } finally {
      setLoadingChats(false);
    }
  };

  const fetchChat = async (id) => {
    try {
      setLoadingChat(true);
      const response = await apiService.getChat(id);
      setActiveChat(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading chat:', err);
      setError('Could not load chat. There is currently high user traffic, please try again later.');
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
      const response = await apiService.createChat('New Chat', sessionId);
      
      const newChat = response.data;
      setChats([newChat, ...chats]);
      navigate(`/chats/${newChat.id}`);
    } catch (err) {
      console.error('Error creating new chat:', err);
      setError('Could not create chat. There is currently high user traffic, please try again later.');
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
      await apiService.deleteChat(id);
      setChats(chats.filter(chat => chat.id !== id));
      
      // If the deleted chat is the active one, navigate to home
      if (chatId === id.toString()) {
        navigate('/');
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
      setError('Could not delete chat. There is currently high user traffic, please try again later.');
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
      const response = await apiService.sendMessage(activeChat.id, userMessage);
      
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
      setError('Could not send message. There is currently high user traffic, please try again later.');
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

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const renderSidebar = () => (
    <Sidebar
      chats={chats}
      loadingChats={loadingChats}
      sessionId={sessionId}
      chatId={chatId}
      collapsed={sidebarCollapsed}
      onCreateNewChat={handleCreateNewChat}
      onSelectChat={handleSelectChat}
      onDeleteChat={handleDeleteChat}
      onToggleCollapse={toggleSidebar}
    />
  );

  const renderWelcomeScreen = () => (
    <WelcomeScreen onStartNewChat={handleStartNewChatFromWelcome} />
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
          height: '70vh',
          position: 'relative',
          pl: { xs: 0, md: 3 }
        }}
      >
        
        
        {/* Messages Area */}
        <Paper
          sx={{ 
            flexGrow: 1, 
            overflowY: 'auto', 
            mb: 2,
            p: 3,
            bgcolor: 'rgba(255, 255, 255, 0.9)',
            borderRadius: 3,
            boxShadow: '0 2px 10px rgba(30, 58, 138, 0.1)',
            border: '1px solid rgba(30, 58, 138, 0.1)',
            '&::-webkit-scrollbar': {
              width: '6px'
            },
            '&::-webkit-scrollbar-track': {
              background: 'rgba(0,0,0,0.05)',
              borderRadius: '3px'
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'rgba(30, 58, 138, 0.3)',
              borderRadius: '3px',
              '&:hover': {
                background: 'rgba(30, 58, 138, 0.5)'
              }
            }
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
                  bgcolor: '#1e3a8a', 
                  mb: 2,
                  width: 56,
                  height: 56
                }}
              >
                <BotIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="body1" color="text.secondary" textAlign="center">
                Hello! I'm Ventana a la Verdad.<br />
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
                      bgcolor: '#1e3a8a', 
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
                  p: 2.5, 
                  borderRadius: 3,
                  bgcolor: msg.is_bot ? 'rgba(248, 250, 252, 0.9)' : '#1e3a8a',
                  color: msg.is_bot ? 'text.primary' : 'white',
                  boxShadow: msg.is_bot ? '0 2px 8px rgba(30, 58, 138, 0.1)' : '0 2px 8px rgba(30, 58, 138, 0.3)',
                  order: msg.is_bot ? 2 : 1,
                  border: msg.is_bot ? '1px solid rgba(30, 58, 138, 0.1)' : 'none'
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
                                  color: '#1e3a8a',
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
                              sx={{                              fontWeight: 'bold',
                              color: '#1e3a8a',
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
                                    borderLeft: '4px solid #1e3a8a',
                                    borderRadius: '0 4px 4px 0',
                                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                  }}
                                >
                                  <Typography 
                                    variant="body2" 
                                    sx={{ 
                                      fontWeight: 'bold',
                                      color: '#1e3a8a',
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
                                          color: '#1e3a8a',
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
                                        color: '#1e3a8a',
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
            p: 2.5,
            mt: 'auto',
            backgroundColor: 'rgba(248, 250, 252, 0.9)',
            borderRadius: 3,
            border: '1px solid rgba(30, 58, 138, 0.1)'
          }}
        >
          <TextField
            fullWidth
            placeholder="Write your question...Example: What is the Truth Commission?"
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
                  sx={{ 
                    ml: 1, 
                    borderRadius: 2,
                    backgroundColor: '#917D26',
                    '&:hover': {
                      backgroundColor: '#7A6A20'
                    }
                  }}
                >
                  {sending ? <CircularProgress size={24} /> : 'Send'}
                </Button>
              ),
              sx: { 
                pr: 1,
                borderRadius: 3,
                backgroundColor: 'white'
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3
              }
            }}
          />
        </Box>
      </Box>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <WindowContainer>
        {renderSidebar()}
        <Box sx={{ flex: 1 }}>
          {error && (
            <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(239, 68, 68, 0.1)', borderRadius: 2 }}>
              <Typography color="error">
                {error}
              </Typography>
            </Box>
          )}
          
          {chatId ? renderChatInterface() : renderWelcomeScreen()}
        </Box>
      </WindowContainer>
    </Container>
  );
};

export default UnifiedChatInterface;
