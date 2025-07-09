import React from 'react';
import { Box, Typography, Button, IconButton, CircularProgress, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon 
} from '@mui/icons-material';

const SidebarRoot = styled(Box)(({ theme, collapsed }) => ({
  background: 'rgba(248, 250, 252, 0.95)',
  borderRight: '1px solid #e2e8f0',
  backdropFilter: 'blur(10px)',
  width: collapsed ? '60px' : '300px',
  padding: theme.spacing(2.5),
  borderRadius: '8px 0 0 8px',
  transition: 'width 0.3s ease',
  overflow: 'hidden',
  [theme.breakpoints.down('md')]: {
    width: collapsed ? '0px' : '100%',
    padding: collapsed ? 0 : theme.spacing(2.5),
    borderRight: 'none',
    borderBottom: collapsed ? 'none' : '1px solid #e2e8f0',
    borderRadius: collapsed ? '0' : '8px 8px 0 0',
    marginBottom: collapsed ? 0 : theme.spacing(2),
    position: collapsed ? 'absolute' : 'relative',
    left: collapsed ? '-100%' : '0',
    zIndex: collapsed ? -1 : 1
  }
}));

const SidebarTitle = styled(Typography)(({ theme }) => ({
  margin: 0,
  marginBottom: theme.spacing(2),
  fontSize: '1.2rem',
  color: '#1e3a8a',
  fontWeight: 700
}));

const SessionInfo = styled(Box)(({ theme }) => ({
  fontSize: '0.9rem',
  color: '#64748b',
  marginBottom: theme.spacing(2),
  padding: theme.spacing(1, 1.5),
  background: 'rgba(30, 58, 138, 0.05)',
  borderRadius: '6px',
  borderLeft: '3px solid #1e3a8a'
}));

const NewChatButton = styled(Button)(({ theme }) => ({
  backgroundColor: '#917D26',
  color: 'white',
  border: 'none',
  padding: theme.spacing(1.5, 2),
  borderRadius: '8px',
  width: '100%',
  fontWeight: 600,
  fontSize: '14px',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-1px)',
    boxShadow: '0 4px 12px rgba(145, 125, 38, 0.3)',
    backgroundColor: '#7A6A20'
  }
}));

const NoChatsMessage = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  color: '#64748b',
  fontSize: '0.9rem',
  marginTop: theme.spacing(3),
  lineHeight: 1.5,
  padding: theme.spacing(2),
  background: 'rgba(248, 250, 252, 0.8)',
  borderRadius: '6px',
  border: '1px dashed #cbd5e1'
}));

const ChatItem = styled(Box)(({ theme, isActive }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  borderRadius: '8px',
  backgroundColor: isActive ? 'rgba(30, 58, 138, 0.1)' : 'transparent',
  cursor: 'pointer',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  transition: 'all 0.2s ease',
  border: isActive ? '1px solid rgba(30, 58, 138, 0.2)' : '1px solid transparent',
  '&:hover': {
    backgroundColor: isActive ? 'rgba(30, 58, 138, 0.15)' : 'rgba(30, 58, 138, 0.05)',
    borderColor: 'rgba(30, 58, 138, 0.2)'
  }
}));

const ChatListContainer = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(2),
  overflowY: 'auto',
  maxHeight: '50vh',
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
}));

const Sidebar = ({ 
  chats, 
  loadingChats, 
  sessionId, 
  chatId, 
  collapsed,
  onCreateNewChat, 
  onSelectChat, 
  onDeleteChat,
  onToggleCollapse 
}) => {
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <SidebarRoot collapsed={collapsed}>
      {/* Collapse/Expand button */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: collapsed ? 'center' : 'space-between', 
        alignItems: 'center',
        mb: collapsed ? 0 : 2
      }}>
        {!collapsed && (
          <SidebarTitle variant="h6">
            Chats
          </SidebarTitle>
        )}        <IconButton
          onClick={onToggleCollapse}
          size="small"
          sx={{
            color: '#1e3a8a',
            backgroundColor: 'rgba(30, 58, 138, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(30, 58, 138, 0.2)',
            }
          }}
        >
          {collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Box>
      
      {!collapsed && (
        <>
          {/* Session indicator (only visible in development) */}
          {process.env.NODE_ENV === 'development' && (
            <SessionInfo>
              Session: {sessionId.slice(-8)}
            </SessionInfo>
          )}
          
          <NewChatButton 
            variant="contained" 
            onClick={onCreateNewChat}
            startIcon={<AddIcon />}
          >
            New Chat
          </NewChatButton>
          
          <ChatListContainer>
            {loadingChats ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress size={24} sx={{ color: '#1e3a8a' }} />
              </Box>
            ) : chats.length === 0 ? (
              <NoChatsMessage>
                No chats yet. Create a new one to get started.
              </NoChatsMessage>
            ) : (
              <>
                {chats.map(chat => (
                  <ChatItem 
                    key={chat.id}
                    isActive={chatId === chat.id.toString()}
                    onClick={() => onSelectChat(chat.id)}
                  >
                    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                      <Typography 
                        variant="body2" 
                        noWrap 
                        sx={{ 
                          maxWidth: 180,
                          fontWeight: chatId === chat.id.toString() ? 600 : 400,
                          color: chatId === chat.id.toString() ? '#1e3a8a' : '#374151'
                        }}
                      >
                        {chat.title}
                      </Typography>
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          color: '#64748b',
                          fontSize: '0.75rem'
                        }}
                      >
                        {formatDate(chat.created_at)}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => onDeleteChat(chat.id, e)}
                      sx={{ 
                        opacity: 0.6,
                        color: '#64748b',
                        '&:hover': { 
                          opacity: 1, 
                          color: '#ef4444',
                          backgroundColor: 'rgba(239, 68, 68, 0.1)'
                        } 
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </ChatItem>
                ))}
              </>
            )}
          </ChatListContainer>
        </>
      )}
      
      {/* Collapsed state - show only a "+" button for new chat */}
      {collapsed && (
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          gap: 1,
          mt: 2
        }}>
          <IconButton
            onClick={onCreateNewChat}
            sx={{
              backgroundColor: '#917D26',
              color: 'white',
              '&:hover': {
                backgroundColor: '#7A6A20',
              },
              width: 40,
              height: 40
            }}
          >
            <AddIcon />
          </IconButton>
        </Box>
      )}
    </SidebarRoot>
  );
};

export default Sidebar;
