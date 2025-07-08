import React from 'react';
import { Container, Typography, Box, Grid, Paper, Link } from '@mui/material';

const About = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
        Welcome to Window to Truth!
      </Typography>
      
      <Grid container spacing={6}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, borderRadius: 2 }}>
            <Typography variant="body1" paragraph>
              Window to Truth is a chatbot that provides reliable and insightful information about the Colombian conflict and peace process.
            </Typography>
            
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4 }}>
              How It Works
            </Typography>
            
            <Typography variant="body1" paragraph>
              Ask about the Colombian conflict, peace agreements, or key events. The chatbot provides accurate context using official data from the Colombian Truth Commission.
            </Typography>
            
            <Typography variant="body1" paragraph>
              Some responses can be near 20 seconds. Please be patient while the chatbot processes your request.
            </Typography>
            
            <Typography variant="body1" paragraph>
              Our answers include references to ensure the information you receive is reliable and precise. We summarize complex issues to make them easier to understand while providing the necessary depth. You are welcome to ask follow-up questions, and the conversation can continue exploring related topics.
            </Typography>
            
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4 }}>
              Resources
            </Typography>
            
            <Typography variant="body1" paragraph>
              For further reading, explore the full: {' '}
              <Link 
                href="https://comisiondelaverdad.co/en" 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ fontWeight: 500 }}
              >
                Colombian Truth Commission Report
              </Link>.
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 4, borderRadius: 2, mb: 4 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              About the Truth Commission
            </Typography>
            
            <Typography variant="body1" paragraph>
              The Commission for the Clarification of Truth, Coexistence, and Non-Repetition was established as part of the 2016 Peace Agreement between the Colombian government and the FARC.
            </Typography>
            
            <Typography variant="body1">
              Their work between 2018 and 2022 has been crucial for understanding the armed conflict and promoting reconciliation throughout Colombia.
            </Typography>
          </Paper>
          
    
        </Grid>
      </Grid>
    </Container>
  );
};

export default About;
