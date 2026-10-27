import React from 'react';
import { Box, Typography, Button, IconButton, CircularProgress, Tooltip } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { styled } from '@mui/material/styles';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon 
} from '@mui/icons-material';

const SidebarRoot = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'collapsed' && prop !== 'inDrawer'
})(({ theme, collapsed, inDrawer }) => ({
  background: 'rgba(248, 250, 252, 0.95)',
  borderRight: '1px solid #e2e8f0',
  backdropFilter: 'blur(10px)',
  // Desktop: collapsible column. Mobile/tablet: full-height panel inside a Drawer
  width: inDrawer ? '18.75rem' : (collapsed ? '3.75rem' : '18.75rem'),
  maxWidth: inDrawer ? '85vw' : 'none',
  height: inDrawer ? '100%' : 'auto',
  flexShrink: 0,
  padding: theme.spacing(2.5),
  borderRadius: inDrawer ? 0 : '8px 0 0 8px',
  transition: 'width 0.3s ease',
  overflow: 'hidden',
  display: inDrawer ? 'flex' : 'block',
  flexDirection: 'column'
}));

const SidebarTitle = styled(Typography)(({ theme }) => ({
  margin: 0,
  marginBottom: theme.spacing(2),
  fontSize: '1.2rem',
  color: '#1e3a8a',
  fontWeight: 700
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

const ChatListContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'inDrawer'
})(({ theme, inDrawer }) => ({
  marginTop: theme.spacing(2),
  overflowY: 'auto',
  maxHeight: inDrawer ? 'none' : '50vh',
  flex: inDrawer ? 1 : 'none',
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
  chatId, 
  collapsed,
  inDrawer = false,
  onCreateNewChat, 
  onSelectChat, 
  onDeleteChat,
  onToggleCollapse 
}) => {
  const { t, i18n } = useTranslation();

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString(i18n.language === 'es' ? 'es-CO' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <SidebarRoot collapsed={collapsed} inDrawer={inDrawer}>
      {/* Collapse/Expand button */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: collapsed ? 'center' : 'space-between', 
        alignItems: 'center',
        mb: collapsed ? 0 : 2
      }}>
        {!collapsed && (
          <SidebarTitle variant="h6">
            {t('sidebar.title')}
          </SidebarTitle>
        )}        <IconButton
          onClick={onToggleCollapse}
          aria-label={collapsed ? t('sidebar.expand') : t('sidebar.collapse')}
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
          <NewChatButton 
            variant="contained" 
            onClick={onCreateNewChat}
            startIcon={<AddIcon />}
          >
            {t('sidebar.newChat')}
          </NewChatButton>
          
          <ChatListContainer inDrawer={inDrawer}>
            {loadingChats ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress size={24} sx={{ color: '#1e3a8a' }} />
              </Box>
            ) : chats.length === 0 ? (
              <NoChatsMessage>
                {t('sidebar.empty')}
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
                          maxWidth: '100%',
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
                      aria-label={t('sidebar.delete')}
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
            aria-label={t('sidebar.newChat')}
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
