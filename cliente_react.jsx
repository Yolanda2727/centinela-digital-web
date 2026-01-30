/**
 * Cliente React para Centinela Digital API
 * npm install axios react-router-dom
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

// ========================
// Servicio de API
// ========================

const API = {
  login: (username, password) =>
    axios.post(`${API_URL}/api/auth/login`, { username, password }),
  
  register: (username, password, email) =>
    axios.post(`${API_URL}/api/auth/register`, { username, password, email }),
  
  analyze: (token, rol, tipo_producto, evidencias) =>
    axios.post(`${API_URL}/api/analyze`, 
      { rol, tipo_producto, evidencias },
      { headers: { 'Authorization': `Bearer ${token}` } }
    ),
  
  batchAnalyze: (token, casos) =>
    axios.post(`${API_URL}/api/batch/analyze`,
      { casos },
      { headers: { 'Authorization': `Bearer ${token}` } }
    ),
  
  getCases: (token) =>
    axios.get(`${API_URL}/api/cases`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    ),
  
  getMetrics: (token) =>
    axios.get(`${API_URL}/api/metrics/institutional`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    ),
  
  getTemporal: (token, period = 'daily') =>
    axios.get(`${API_URL}/api/metrics/temporal?period=${period}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
};

// ========================
// Componente: Login
// ========================

function LoginComponent({ onLogin }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await API.login(username, password);
      onLogin(response.data.token, username);
    } catch (err) {
      setError(err.response?.data?.error || 'Error de login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1>🔐 Centinela Digital</h1>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Autenticando...' : 'Iniciar Sesión'}
          </button>
          {error && <p style={styles.error}>{error}</p>}
        </form>
        <p style={styles.hint}>Demo: admin / admin123</p>
      </div>
    </div>
  );
}

// ========================
// Componente: Análisis
// ========================

function AnalysisComponent({ token, onLogout }) {
  const [rol, setRol] = useState('Estudiante');
  const [tipoProducto, setTipoProducto] = useState('Ensayo');
  const [evidencias, setEvidencias] = useState({
    estilo_diferente: 0,
    tiempo_sospechoso: 0,
    referencias_raras: 0,
    datos_inconsistentes: 0,
    imagenes_sospechosas: 0,
    sin_borradores: 0,
    defensa_debil: 0,
  });
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await API.analyze(token, rol, tipoProducto, evidencias);
      setResultado(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error en análisis');
    } finally {
      setLoading(false);
    }
  };

  const toggleEvidence = (key) => {
    setEvidencias(prev => ({
      ...prev,
      [key]: prev[key] ? 0 : 1
    }));
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'BAJO': return '#4CAF50';
      case 'MEDIO': return '#FF9800';
      case 'ALTO': return '#F44336';
      default: return '#757575';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>📊 Análisis de Integridad Académica</h1>
        <button onClick={onLogout} style={styles.logoutBtn}>Salir</button>
      </div>

      <div style={styles.grid}>
        {/* Formulario */}
        <div style={styles.card}>
          <h2>Formulario de Análisis</h2>
          <form onSubmit={handleAnalyze}>
            <div style={styles.formGroup}>
              <label>Rol del usuario:</label>
              <select
                value={rol}
                onChange={(e) => setRol(e.target.value)}
                style={styles.select}
              >
                <option>Estudiante</option>
                <option>Docente-investigador</option>
                <option>Coinvestigador externo</option>
              </select>
            </div>

            <div style={styles.formGroup}>
              <label>Tipo de producto:</label>
              <select
                value={tipoProducto}
                onChange={(e) => setTipoProducto(e.target.value)}
                style={styles.select}
              >
                <option>Ensayo</option>
                <option>Tesis</option>
                <option>Artículo científico</option>
                <option>Informe técnico</option>
              </select>
            </div>

            <div style={styles.formGroup}>
              <label>Evidencias de alerta:</label>
              {Object.entries(evidencias).map(([key, value]) => (
                <label key={key} style={styles.checkbox}>
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={() => toggleEvidence(key)}
                  />
                  {key.replace(/_/g, ' ')}
                </label>
              ))}
            </div>

            <button type="submit" disabled={loading} style={styles.button}>
              {loading ? 'Analizando...' : 'Analizar'}
            </button>
            {error && <p style={styles.error}>{error}</p>}
          </form>
        </div>

        {/* Resultado */}
        {resultado && (
          <div style={styles.card}>
            <h2>📋 Resultado del Análisis</h2>
            <div style={{
              ...styles.resultBox,
              borderLeft: `5px solid ${getRiskColor(resultado.analysis.overall_level)}`
            }}>
              <div style={styles.resultRow}>
                <span>Score:</span>
                <strong style={{ color: getRiskColor(resultado.analysis.overall_level) }}>
                  {resultado.analysis.overall_score}/100
                </strong>
              </div>
              <div style={styles.resultRow}>
                <span>Nivel de Riesgo:</span>
                <strong style={{ color: getRiskColor(resultado.analysis.overall_level) }}>
                  {resultado.analysis.overall_level}
                </strong>
              </div>
              <div style={styles.resultRow}>
                <span>Confianza:</span>
                <strong>{(resultado.analysis.confidence * 100).toFixed(1)}%</strong>
              </div>
              
              <h3>Recomendaciones:</h3>
              <ul>
                {resultado.analysis.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>

              <p style={styles.caseId}>
                <small>Case ID: {resultado.case_id}</small>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ========================
// App Principal
// ========================

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [username, setUsername] = useState(localStorage.getItem('username'));

  const handleLogin = (newToken, newUsername) => {
    setToken(newToken);
    setUsername(newUsername);
    localStorage.setItem('token', newToken);
    localStorage.setItem('username', newUsername);
  };

  const handleLogout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  };

  return (
    <div>
      {token ? (
        <AnalysisComponent token={token} onLogout={handleLogout} />
      ) : (
        <LoginComponent onLogin={handleLogin} />
      )}
    </div>
  );
}

// ========================
// Estilos
// ========================

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    borderBottom: '2px solid #ddd',
    paddingBottom: '20px',
  },
  logoutBtn: {
    padding: '10px 20px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '20px',
  },
  card: {
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  formGroup: {
    marginBottom: '15px',
  },
  input: {
    width: '100%',
    padding: '10px',
    marginBottom: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
  },
  select: {
    width: '100%',
    padding: '10px',
    marginTop: '5px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
  },
  checkbox: {
    display: 'block',
    marginBottom: '8px',
    cursor: 'pointer',
  },
  button: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  },
  error: {
    color: '#f44336',
    marginTop: '10px',
    fontSize: '14px',
  },
  hint: {
    color: '#999',
    fontSize: '12px',
    marginTop: '10px',
  },
  resultBox: {
    backgroundColor: '#f5f5f5',
    padding: '15px',
    borderRadius: '4px',
  },
  resultRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px',
    padding: '10px 0',
    borderBottom: '1px solid #ddd',
  },
  caseId: {
    marginTop: '15px',
    paddingTop: '15px',
    borderTop: '1px solid #ddd',
    color: '#999',
  },
};

export default App;
