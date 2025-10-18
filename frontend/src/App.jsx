import { useState } from 'react'
import './App.css'

function App() {
  const [profileDescription, setProfileDescription] = useState('');
  const [response, setResponse] = useState(null);

  const handleSubmit = async () => {
    try {
      const res = await fetch('http://localhost:8001/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_profile: profileDescription,
          language: 'all',
          per_page: 20,
          top_n: 100,
          model: 'all-MiniLM-L6-v2'
        })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      setResponse(data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      alert('Failed to fetch recommendations: ' + error.message);
    }
  }

  return (
    <>
      <div>
        <h1>Github Issues Recommendation Engine</h1>
        <p>This application recommends Github issues based on the skills you present in your profile description.</p>
        <p>Get started by entering your profile description below:</p>
        <textarea
          placeholder="Enter your profile description here..."
          rows="10"
          cols="50"
          onChange={(e) => setProfileDescription(e.target.value)}
        ></textarea>
        <br />
        <button onClick={handleSubmit}>Get Recommendations</button>

        <div id="recommendations">
          {response && response.map((issue, index) => (
            <div key={index} className="recommendation-card">
              <h3>{issue.title}</h3>
              <p><strong>{issue.repo}</strong></p>
              <a href={issue.url} target="_blank" rel="noopener noreferrer">View on GitHub →</a>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
export default App