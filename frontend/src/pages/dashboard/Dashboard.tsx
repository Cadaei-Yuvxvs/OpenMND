import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useQuery } from '@tanstack/react-query';
import { paperService } from '../../services/api';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const StatCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(2),
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
}));

const Dashboard = () => {
  const { data: papers, isLoading } = useQuery({
    queryKey: ['papers'],
    queryFn: () => paperService.getPapers(0, 100),
    refetchInterval: 30000,
  });

  const totalPapers = papers?.length || 0;
  const avgSentiment = papers?.reduce((acc, paper) => 
    acc + (paper.sentiment_score || 5), 0) / totalPapers || 5;
  const processedPapers = papers?.filter(paper => paper.summary).length || 0;

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        OpenMND Research Intelligence Dashboard
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Real-time analysis of Motor Neuron Disease research trends and insights
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent>
              <Typography variant="h4" component="div">
                {totalPapers}
              </Typography>
              <Typography variant="body2">
                Total Papers
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent>
              <Typography variant="h4" component="div">
                {processedPapers}
              </Typography>
              <Typography variant="body2">
                AI Processed
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent>
              <Typography variant="h4" component="div">
                {avgSentiment.toFixed(1)}
              </Typography>
              <Typography variant="body2">
                Avg Optimism Score
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent>
              <Typography variant="h4" component="div">
                {new Date().getFullYear()}
              </Typography>
              <Typography variant="body2">
                Current Year
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>

        <Grid item xs={12} lg={8}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Research Trends Over Time
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
              <Typography variant="body2" color="text.secondary">
                Chart component coming soon
              </Typography>
            </Box>
          </StyledPaper>
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Research Theme Distribution
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
              <Typography variant="body2" color="text.secondary">
                Chart component coming soon
              </Typography>
            </Box>
          </StyledPaper>
        </Grid>

        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Recently Added Papers
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200 }}>
              <Typography variant="body2" color="text.secondary">
                Recent papers component coming soon
              </Typography>
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;