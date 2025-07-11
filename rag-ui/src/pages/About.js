import React from 'react';
import { Container, Typography, Box, Grid, Paper, Link } from '@mui/material';
import WindowContainer from '../components/WindowContainer';

const About = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <WindowContainer>
        <Grid container spacing={6} justifyContent="center" alignItems="stretch">
        <Grid item xs={12} md={8} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Paper sx={{ p: 2, borderRadius: 2, mb: 4, textAlign: 'center', flex: 1, minHeight: 210 }}>
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4, textAlign: 'center' }}>
                Welcome
              </Typography>
              <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
                Ventana a la Verdad is a chatbot that provides reliable and insightful information about the Colombian armed conflict and peace processes according to the work done by the Colombian Truth Commission (2019–2022).
                The chatbot is an innovation in progress created in collaboration by the University of Notre Dame and the University Javeriana within the framework of the Legacy project.
                This chatbot is the result of a joint initiative between the University of Notre Dame, specifically the Lucy Family Institute for Data & Society and the Kroc Institute, and the Pontificia Universidad Javeriana. This is partly funded by the IBM Tech Ethics Lab.
              </Typography>
            </Paper>
            <Paper sx={{ p: 2, borderRadius: 2, mb: 0, textAlign: 'center', flex: 1, minHeight: 210 }}>
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4, textAlign: 'center' }}>
                How It Works
              </Typography>
              <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
                Ask about the Colombian armed conflict, peace agreements, or key actors and historical events. The chatbot provides accurate context using official public data released by the Colombian Truth Commission.
              </Typography>
              <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
                Some responses can take up to 20 seconds, so please be patient while the chatbot processes your request.
              </Typography>
              <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
                The answers include references to ensure that you can compare the information with the original sources directly. We summarize complex issues to make them easier to understand, while the sources can offer you more depth.
              </Typography>
              <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
                You are welcome to ask for shorter or longer answers, request clarifications, or ask for bullet points or numerical lists.
              </Typography>
            </Paper>
          </Box>
        </Grid>
        
        <Grid item xs={12} md={4} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Paper sx={{ p: 2, borderRadius: 2, mb: 4, textAlign: 'center', flex: 1, minHeight: 210 }}>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4, textAlign: 'center' }}>
              Resources
            </Typography>
            
            <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
              For further reading, explore the full: {' '}
              <Link 
                href="https://comisiondelaverdad.co/en" 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ fontWeight: 500 }}
              >
                Colombian Truth Commission Report
              </Link>
              {' '} and {' '}
              <Link 
                href="https://legacyproject.nd.edu/" 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ fontWeight: 500 }}
              >
                The Legacy Project
              </Link>.
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4, textAlign: 'center' }}>
              Contact
            </Typography>
            
            <Typography variant="body1" paragraph sx={{ textAlign: 'center' }}>
              PhD Luis Gabriel Moreno Sandoval
              morenoluis@javeriana.edu.co
            </Typography>
          </Paper>
            <Paper sx={{ p: 2, borderRadius: 2, mb: 0, textAlign: 'left', flex: 1, minHeight: 210 }}>
                       
            <Typography variant="body1" paragraph sx={{ textAlign: 'left', mb: 2 }}>
              <ul style={{ paddingLeft: '1.2em', margin: 0 }}>
                <li><strong>Project:</strong> Cultural Context-Aware Question-Answering System for the Colombian Truth Commission</li>
                <li><strong>Funding:</strong> Notre Dame–IBM Technology Ethics Lab</li>
                <li><strong>Call:</strong> 2024 CFP: The Ethics of Large-Scale Models</li>
                <li><strong>Amount awarded:</strong> USD $60,000</li>
                <li><strong>Period:</strong> Until July 2025</li>
              </ul>
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Box sx={{ display: 'inline-block', width: '100%', maxWidth: '320px', mx: 'auto' }}>
                  <Link 
                    href="https://ethics.nd.edu/labs-and-centers/notre-dame-ibm-technology-ethics-lab/"
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ 
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: '#14284B',
                      borderRadius: 2,
                      p: 2,
                      minHeight: '70px',
                      width: '100%',
                      '&:hover': { opacity: 0.8 }
                    }}
                  >
                    <img 
                      src="/logo_ethics.svg"
                      alt="Notre Dame IBM Technology Ethics Lab"
                      style={{ 
                        height: '48px',
                        maxWidth: '100%',
                        width: 'auto',
                        margin: '0 auto',
                        display: 'block'
                      }}
                    />
                  </Link>
                </Box>
              </Box>
            </Typography>
          </Paper>
          
            </Box>
        </Grid>
      </Grid>
      </WindowContainer>
    </Container>
  );
};

export default About;
