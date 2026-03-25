import { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Button } from '../../components/ui/Button';
import { Send, Loader2, FileText } from 'lucide-react';

export const InterviewSession = () => {
  const { session_id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [chat, setChat] = useState([]);
  const [currentPhase, setCurrentPhase] = useState("Initializing...");
  const [currentTopic, setCurrentTopic] = useState("");
  
  const [inputMessage, setInputMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const endOfChatRef = useRef(null);

  // Initialize from router state
  useEffect(() => {
    if (location.state?.initialSession) {
      const init = location.state.initialSession;
      if (init.current_question) {
        setChat([{ role: 'ai', content: init.current_question }]);
        setCurrentPhase(init.current_phase_name || "Getting Started");
        setCurrentTopic(init.current_topic_id || "");
      }
    } else {
      // If we land here without state, the backend lacks a standalone GET status endpoint for the initial question.
      // We could add an error redirect or a default message.
      setChat([{ role: 'ai', content: "Welcome. Please press 'Ready' to begin." }]);
    }
  }, [location.state]);

  const autoScroll = () => {
    endOfChatRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    autoScroll();
  }, [chat, isProcessing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isProcessing) return;

    const userMsg = inputMessage.trim();
    setChat(prev => [...prev, { role: 'user', content: userMsg }]);
    setInputMessage("");
    setIsProcessing(true);
    setError(null);

    try {
      const response = await api.submitAnswer(session_id, userMsg);
      // Wait for AI to respond
      if (response.current_question) {
        setChat(prev => [...prev, { role: 'ai', content: response.current_question }]);
        setCurrentPhase(response.current_phase_name || currentPhase);
        setCurrentTopic(response.current_topic_id || currentTopic);
      } else {
         // Transition to Report page if the backend didn't return a question (interview over)
         navigate(`/report/${session_id}`);
      }
    } catch (err) {
      setError(err.message || 'Failed to submit answer');
      // Revert optimism if failed
      setChat(prev => prev.slice(0, -1));
      setInputMessage(userMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 70px)' }}>
      {/* Sidebar: Interview Pulse */}
      <div style={{ width: '300px', borderRight: '1px solid var(--border-color)', backgroundColor: '#FFFFFF', padding: '24px', display: 'flex', flexDirection: 'column' }}>
        <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '1px', marginBottom: '24px' }}>
          Interview Pulse
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1 }}>
          <div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Current Phase</p>
            <p style={{ fontSize: '16px', fontWeight: 500, color: 'var(--text-primary)' }}>{currentPhase}</p>
          </div>
          <div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Active Topic</p>
            <p style={{ fontSize: '15px', color: 'var(--text-primary)' }}>{currentTopic || '---'}</p>
          </div>
        </div>

        <div style={{ marginTop: 'auto', paddingTop: '24px', borderTop: '1px solid var(--border-color)' }}>
          <Button fullWidth onClick={() => navigate(`/report/${session_id}`)}>
            <FileText size={16} style={{ marginRight: '8px' }} /> End & Generate Report
          </Button>
        </div>
      </div>

      {/* Main Chat Canvas */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-secondary)', position: 'relative' }}>
        
        {/* Chat History */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '40px' }}>
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {chat.map((msg, idx) => (
              <div key={idx} style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
              }}>
                <div style={{
                  maxWidth: '75%',
                  padding: '16px 20px',
                  borderRadius: '12px',
                  backgroundColor: msg.role === 'user' ? 'var(--accent-primary)' : '#FFFFFF',
                  color: msg.role === 'user' ? '#FFFFFF' : 'var(--text-primary)',
                  boxShadow: 'var(--shadow-sm)',
                  lineHeight: '1.6',
                  fontSize: '16px',
                  border: msg.role === 'ai' ? '1px solid var(--border-color)' : 'none'
                }}>
                  {msg.content}
                </div>
              </div>
            ))}
            
            {isProcessing && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  padding: '16px 20px', borderRadius: '12px', backgroundColor: '#FFFFFF',
                  border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)'
                }}>
                  <Loader2 size={16} className="lucide-spin" style={{ animation: 'spin 1.5s linear infinite' }} /> AI is Thinking...
                </div>
              </div>
            )}
            <div ref={endOfChatRef} />
          </div>
        </div>

        {/* Input Area */}
        <div style={{ padding: '24px 40px', backgroundColor: '#FFFFFF', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
             {error && <div style={{ color: '#EF4444', fontSize: '14px', marginBottom: '8px' }}>{error}</div>}
             <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
                <textarea 
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your answer here..."
                  disabled={isProcessing}
                  style={{
                    flex: 1, padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)',
                    fontSize: '16px', fontFamily: 'inherit', resize: 'none', height: '60px', outline: 'none',
                    transition: 'border-color 0.2s', backgroundColor: 'var(--bg-secondary)'
                  }}
                  onFocus={(e) => e.target.style.borderColor = 'var(--accent-primary)'}
                  onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                />
                <Button type="submit" disabled={isProcessing || !inputMessage.trim()}>
                  <Send size={18} /> Send
                </Button>
             </form>
          </div>
        </div>

      </div>
      
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default InterviewSession;
