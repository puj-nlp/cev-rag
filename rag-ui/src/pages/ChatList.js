import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Container, Typography, Grid, Box, Button, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, CircularProgress, List, ListItem
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { apiService } from '../services/api';

const ChatList = () => {
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');

  // Cargar la lista de chats
  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/chats`);
      setChats(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading chats:', err);
      setError('Could not load chats. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewChatTitle('');
  };

  const handleCreateChat = async () => {
    try {
      const response = await axios.post(`${API_URL}/chats`, {
        title: newChatTitle || 'New Chat'
      });
      
      setChats([...chats, response.data]);
      handleCloseDialog();
      navigate(`/chats/${response.data.id}`);
    } catch (err) {
      console.error('Error creating chat:', err);
      setError('Could not create chat. Please try again.');
    }
  };

  const handleNewChat = () => {
    handleCreateChat();
  };

  const handleDeleteChat = async (chatId, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this chat?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/chats/${chatId}`);
      setChats(chats.filter(chat => chat.id !== chatId));
    } catch (err) {
      console.error('Error deleting chat:', err);
      setError('Could not delete chat. Please try again.');
    }
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
              onClick={handleNewChat}
              startIcon={<AddIcon />}
            >
              New Chat
            </Button>
            
            <Box sx={{ mt: 2 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : chats.length === 0 ? (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
                  No chats yet. Create a new one to start.
                </Typography>
              ) : (
                <List disablePadding>
                  {chats.map(chat => (
                    <ListItem 
                      key={chat.id}
                      disablePadding
                      sx={{ display: 'block', mb: 0.5 }}
                    >
                      <Box 
                        component={Link}
                        to={`/chats/${chat.id}`}
                        sx={{ 
                          p: 1.5, 
                          borderRadius: 1.5,
                          textDecoration: 'none',
                          color: 'text.primary',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          '&:hover': { 
                            backgroundColor: 'rgba(0,0,0,0.04)'
                          }
                        }}
                      >
                        <Box>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 180 }}>
                            {chat.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(chat.created_at)}
                          </Typography>
                        </Box>
                        <DeleteIcon 
                          fontSize="small" 
                          color="action"
                          onClick={(e) => handleDeleteChat(chat.id, e)}
                          sx={{ 
                            opacity: 0.6, 
                            '&:hover': { opacity: 1, color: 'error.main' } 
                          }}
                        />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </Box>
        </Grid>
        
        {/* Main Content */}
        <Grid item xs={12} md={9}>
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
              onClick={handleNewChat}
              sx={{ borderRadius: 2, px: 4, py: 1 }}
            >
              Start New Chat
            </Button>
          </Box>
        </Grid>
      </Grid>
      
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Create New Chat</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Chat Title"
            type="text"
            fullWidth
            variant="outlined"
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleCreateChat} color="primary">Create</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChatList;
