import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Container, Typography, Grid, Card, CardContent, 
  CardActions, Button, Fab, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatList = () => {
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
      console.error('Error al cargar los chats:', err);
      setError('No se pudieron cargar los chats. Por favor, inténtalo de nuevo.');
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
        title: newChatTitle || 'Nueva conversación'
      });
      
      setChats([...chats, response.data]);
      handleCloseDialog();
    } catch (err) {
      console.error('Error al crear el chat:', err);
      setError('No se pudo crear el chat. Por favor, inténtalo de nuevo.');
    }
  };

  const handleDeleteChat = async (chatId, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!window.confirm('¿Estás seguro de que quieres eliminar este chat?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/chats/${chatId}`);
      setChats(chats.filter(chat => chat.id !== chatId));
    } catch (err) {
      console.error('Error al eliminar el chat:', err);
      setError('No se pudo eliminar el chat. Por favor, inténtalo de nuevo.');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mt: 4 }}>
        Conversaciones
      </Typography>
      
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      
      <Grid container spacing={3}>
        {loading ? (
          <Typography>Cargando chats...</Typography>
        ) : chats.length === 0 ? (
          <Typography sx={{ mt: 2, ml: 2 }}>No hay conversaciones. Crea una nueva para comenzar.</Typography>
        ) : (
          chats.map(chat => (
            <Grid item xs={12} sm={6} md={4} key={chat.id}>
              <Card component={Link} to={`/chats/${chat.id}`} sx={{ 
                textDecoration: 'none',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 3
                }
              }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="div" noWrap>
                    {chat.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Creado: {formatDate(chat.created_at)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Última actividad: {formatDate(chat.updated_at)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {chat.messages?.length || 0} mensaje(s)
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                  >
                    Eliminar
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))
        )}
      </Grid>
      
      <Fab 
        color="primary" 
        aria-label="add"
        onClick={handleOpenDialog}
        sx={{ 
          position: 'fixed',
          bottom: 16,
          right: 16
        }}
      >
        <AddIcon />
      </Fab>
      
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Crear nueva conversación</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Título de la conversación"
            type="text"
            fullWidth
            variant="outlined"
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button onClick={handleCreateChat} color="primary">Crear</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChatList;
