import React, { useState } from 'react';
import { Container, Grid, Typography, Box, TextField, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const HomePage = () => {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) return;
    
    try {
      // Create a new chat
      const response = await axios.post(`${API_URL}/chats`, {
        title: 'New Chat'
      });
      
      const chatId = response.data.id;
      
      // Send the first message to the chat
      await axios.post(`${API_URL}/chats/${chatId}/messages`, {
        question: question,
        chat_id: chatId
      });
      
      // Navigate to the new chat
      navigate(`/chats/${chatId}`);
    } catch (error) {
      console.error('Error creating chat:', error);
    }
  };

  return (
    <Container>
      <Grid container spacing={4} sx={{ pt: 6, pb: 8 }}>
        {/* Left column - Chats Sidebar */}
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
              onClick={() => navigate('/chats')}
            >
              <Box component="span" sx={{ display: 'flex', alignItems: 'center' }}>
                + New Chat
              </Box>
            </Button>
            
            <Box sx={{ mt: 2 }}>
              <Box 
                sx={{ 
                  p: 1.5, 
                  mb: 1, 
                  borderRadius: 1.5,
                  '&:hover': { backgroundColor: 'rgba(0,0,0,0.04)' },
                  cursor: 'pointer'
                }}
                onClick={() => navigate('/chats/1')}
              >
                <Typography variant="body2">Chat 1</Typography>
              </Box>
              
              <Box 
                sx={{ 
                  p: 1.5, 
                  mb: 1, 
                  borderRadius: 1.5,
                  '&:hover': { backgroundColor: 'rgba(0,0,0,0.04)' },
                  cursor: 'pointer'
                }}
                onClick={() => navigate('/chats/2')}
              >
                <Typography variant="body2">Chat 2</Typography>
              </Box>
            </Box>
          </Box>
        </Grid>
        
        {/* Right column - Main content */}
        <Grid item xs={12} md={9}>
          <Box sx={{ textAlign: 'center', mt: 8, mb: 6 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              Welcome to Window to Truth!
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto', mb: 5 }}>
              Explore testimonies from Colombia's Truth Commission. Ask questions about the testimonies and get answers based on the compiled information.
            </Typography>
          </Box>
          
          <Box sx={{ maxWidth: 700, mx: 'auto', mt: 6 }}>
            <Box sx={{ 
              backgroundColor: '#f9fafb',
              borderRadius: 2,
              p: 2,
              mb: 3
            }}>
              <Typography variant="body1" sx={{ color: 'text.secondary', mb: 1 }}>
                Window to Truth
              </Typography>
              <Box sx={{ backgroundColor: 'white', p: 2, borderRadius: 1, mb: 2 }}>
                <Typography variant="body1">
                  Hello, I'm Window to Truth. What testimonies would you like to learn about today?
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ 
              backgroundColor: '#f9fafb',
              borderRadius: 2,
              p: 2,
              mb: 3,
              textAlign: 'right'
            }}>
              <Typography variant="body1" sx={{ color: 'text.secondary', mb: 1 }}>
                User
              </Typography>
              <Box sx={{ backgroundColor: '#1976d2', color: 'white', p: 2, borderRadius: 1, mb: 2, textAlign: 'left', display: 'inline-block' }}>
                <Typography variant="body1">
                  I want to know about the testimonies of victims of forced displacement.
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ 
              backgroundColor: '#f9fafb',
              borderRadius: 2,
              p: 2
            }}>
              <Typography variant="body1" sx={{ color: 'text.secondary', mb: 1 }}>
                Window to Truth
              </Typography>
              <Box sx={{ backgroundColor: 'white', p: 2, borderRadius: 1, mb: 2 }}>
                <Typography variant="body1">
                  The testimonies of victims of forced displacement reveal the harsh realities of those forced to leave their homes. Many of these stories highlight the loss of land, family disintegration, and the difficulties of rebuilding their lives in new places. Would you like to know about any specific testimony?
                </Typography>
              </Box>
            </Box>
          </Box>
          
          <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 700, mx: 'auto', mt: 6 }}>
            <TextField
              fullWidth
              placeholder="Write your question..."
              variant="outlined"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              InputProps={{
                endAdornment: (
                  <Button type="submit" variant="contained" disabled={!question.trim()}>
                    Send
                  </Button>
                ),
                sx: { pr: 1, borderRadius: 3 }
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                }
              }}
            />
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HomePage;
