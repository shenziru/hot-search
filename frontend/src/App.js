import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Alert, Badge, Button, Spinner, ListGroup, Nav } from 'react-bootstrap';
import './styles.css';

// 配置API端点
const getApiBaseUrl = () => {
  // 如果在开发环境中运行，可能需要不同的API URL
  // 这里自动检测端口，以便更灵活地配置
  const port = 5000;  // 后端默认端口
  const hostname = window.location.hostname;
  const baseUrl = `http://${hostname}:${port}/api`;
  console.log(`API基础URL: ${baseUrl}`);
  return baseUrl;
};

const API_BASE_URL = getApiBaseUrl();
const TOPHUB_DATA_ENDPOINT = `${API_BASE_URL}/hot_data`;
const PREDICTIONS_ENDPOINT = `${API_BASE_URL}/predictions`;
const REFRESH_ENDPOINT = `${API_BASE_URL}/generate_predictions`;
const FETCH_TIMEOUT = 10000; // 请求超时时间（毫秒）
const MAX_RETRIES = 2; // 最大重试次数

function App() {
  // 状态管理
  const [backendConnected, setBackendConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const [hotData, setHotData] = useState({ 科技: [], '大厂八卦职场新闻': [], 'AI工具': [] });
  const [predictions, setPredictions] = useState([]);
  const [predictionDate, setPredictionDate] = useState('未知');
  const [loading, setLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState({ type: 'warning', message: '检查后端连接中...' });
  const [activeNav, setActiveNav] = useState('home');
  const [refreshing, setRefreshing] = useState(false);

  // 检查后端连接
  const checkBackendConnection = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
      
      const response = await fetch(TOPHUB_DATA_ENDPOINT, { signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (response.ok) {
        setBackendConnected(true);
        setConnectionError(false);
        setStatusMessage({ type: 'success', message: '后端已连接' });
        return true;
      } else {
        showConnectionError();
        return false;
      }
    } catch (error) {
      showConnectionError();
      return false;
    }
  };

  // 显示连接错误
  const showConnectionError = () => {
    setBackendConnected(false);
    setConnectionError(true);
    setStatusMessage({ 
      type: 'danger', 
      message: '无法连接到后端服务，请确保后端服务器已启动'
    });
  };

  // 带超时和重试功能的fetch
  const fetchWithTimeout = async (url, options = {}, retries = MAX_RETRIES) => {
    const controller = new AbortController();
    const { signal } = controller;
    
    // 设置超时
    const timeout = setTimeout(() => {
      controller.abort();
    }, FETCH_TIMEOUT);
    
    try {
      const response = await fetch(url, { ...options, signal });
      clearTimeout(timeout);
      return response;
    } catch (error) {
      clearTimeout(timeout);
      
      // 如果是超时或网络错误，且还有重试次数，则重试
      if ((error.name === 'AbortError' || error.name === 'TypeError') && retries > 0) {
        console.log(`请求失败，正在重试... (剩余${retries}次)`);
        return fetchWithTimeout(url, options, retries - 1);
      }
      
      throw error;
    }
  };

  // 加载TopHub数据
  const loadTopHubData = async () => {
    try {
      const response = await fetchWithTimeout(TOPHUB_DATA_ENDPOINT);
      const result = await response.json();
      
      console.log('后端返回的热搜数据:', result);
      
      // 直接使用返回的数据，不需要检查success字段
      setHotData(result);
      setStatusMessage({ type: 'success', message: '热搜数据加载成功' });
    } catch (error) {
      console.error('获取热搜数据出错:', error);
      setStatusMessage({ type: 'danger', message: '无法连接到服务器，请检查网络连接' });
    }
  };

  // 加载预测数据
  const loadPredictions = async () => {
    try {
      const response = await fetchWithTimeout(PREDICTIONS_ENDPOINT);
      const result = await response.json();
      
      console.log('后端返回的预测数据:', result);
      
      // 提取预测数据和日期
      const predictionsData = result.predictions || [];
      const date = result.date || '未知';
      
      // 显示预测日期
      setPredictionDate(date);
      
      console.log('格式化后的预测数据:', predictionsData);
      
      // 处理预测数据，确保是数组格式
      let formattedPredictions = [];
      
      if (Array.isArray(predictionsData)) {
        // 如果已经是数组，直接使用
        formattedPredictions = predictionsData;
      } else if (predictionsData && typeof predictionsData === 'object') {
        // 如果是对象格式，可能是以类别为键的对象
        if (Object.keys(predictionsData).length > 0) {
          // 将对象中的内容转换为数组
          formattedPredictions = Object.entries(predictionsData)
            .flatMap(([category, items]) => {
              // 如果items是数组，给每个项目添加类别标记
              if (Array.isArray(items)) {
                return items.map(item => ({
                  ...item,
                  category
                }));
              }
              return [];
            });
        }
      }
      
      // 设置预测数据
      setPredictions(formattedPredictions);
      setStatusMessage({ type: 'success', message: '预测数据加载成功' });
    } catch (error) {
      console.error('获取预测数据出错:', error);
      setStatusMessage({ type: 'danger', message: '无法连接到服务器，请检查网络连接' });
    }
  };

  // 加载所有数据
  const loadData = async () => {
    setLoading(true);
    const isConnected = await checkBackendConnection();
    
    if (isConnected) {
      await Promise.all([
        loadTopHubData(),
        loadPredictions()
      ]);
    }
    
    setLoading(false);
  };

  // 刷新按钮处理
  const handleRefresh = async () => {
    setRefreshing(true);
    setStatusMessage({ type: 'info', message: '正在刷新数据...' });
    
    try {
      const response = await fetchWithTimeout(REFRESH_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ force: true })
      });
      
      const result = await response.json();
      
      console.log('刷新数据的响应:', result);
      
      if (result.success === true) {
        setStatusMessage({ type: 'success', message: '数据刷新成功！' });
        // 刷新成功后，重新加载数据
        await loadData();
      } else {
        setStatusMessage({ type: 'warning', message: '刷新数据失败: ' + (result.message || '') });
      }
    } catch (error) {
      console.error('刷新数据时出错:', error);
      setStatusMessage({ type: 'danger', message: '刷新数据失败，请稍后再试' });
    } finally {
      setRefreshing(false);
    }
  };

  // 组件挂载后加载数据
  useEffect(() => {
    loadData();
    
    // 导航链接点击事件
    const handleNavClick = (key) => {
      setActiveNav(key);
    };
  }, []);

  // 渲染热搜列表
  const renderHotList = (items) => {
    if (!items || items.length === 0) {
      return <ListGroup.Item className="text-center">暂无数据</ListGroup.Item>;
    }
    
    return items.map((item, index) => (
      <ListGroup.Item key={index}>
        <a href={item.url} target="_blank" rel="noopener noreferrer" className="d-flex">
          <span className="me-2">{index + 1}.</span>
          {item.title}
        </a>
      </ListGroup.Item>
    ));
  };

  // 渲染预测卡片
  const renderPredictions = () => {
    // 确保predictions是数组
    if (!predictions || !Array.isArray(predictions) || predictions.length === 0) {
      console.log('预测数据格式不是数组:', predictions);
      return (
        <Col xs={12} className="text-center">
          <p className="text-muted">暂无预测数据</p>
        </Col>
      );
    }
    
    // 生成随机卡片头部颜色
    const colors = ['primary', 'success', 'info', 'warning', 'danger'];
    
    return predictions.map((prediction, index) => (
      <Col lg={4} md={6} className="mb-4" key={index}>
        <Card className="shadow prediction-card">
          <Card.Header className={`bg-${colors[index % colors.length]} text-white`}>
            <h5 className="card-title mb-0">
              <i className="fas fa-lightbulb me-2"></i>
              {prediction.category ? `${prediction.category} - ` : ''}
              话题 {index + 1}
            </h5>
          </Card.Header>
          <Card.Body>
            {prediction.topic && (
              <>
                <Card.Text>{prediction.topic}</Card.Text>
                <hr />
              </>
            )}
            
            {/* 显示标题 */}
            {prediction.title && (
              <div className="fw-bold mb-3">{prediction.title}</div>
            )}
            
            {/* 显示原因 */}
            {prediction.reason && (
              <div className="text-muted small mb-3">{prediction.reason}</div>
            )}
            
            {/* 如果有titles数组，显示可能的标题 */}
            {prediction.titles && Array.isArray(prediction.titles) && prediction.titles.length > 0 && (
              <>
                <h6 className="mb-3">可能的标题:</h6>
                {prediction.titles.map((title, idx) => (
                  <div className="prediction-title" key={idx}>
                    <i className="fas fa-angle-right me-2"></i>{title}
                  </div>
                ))}
              </>
            )}
          </Card.Body>
        </Card>
      </Col>
    ));
  };

  return (
    <Container className="py-4">
      <h1 className="text-center mb-4">热搜预测系统</h1>
      
      <div className="status-indicator">
        <Alert variant={statusMessage.type} className="d-flex justify-content-between align-items-center">
          <span>{statusMessage.message}</span>
          {backendConnected && (
            <div>
              <Badge bg="info" className="me-2">最后预测: {predictionDate}</Badge>
            </div>
          )}
        </Alert>
        
        {connectionError && (
          <div className="text-center mt-2">
            <Button variant="outline-danger" size="sm" onClick={checkBackendConnection}>
              重试连接
            </Button>
          </div>
        )}
      </div>

      <div className="mb-4 text-center">
        <Button 
          variant="primary" 
          onClick={handleRefresh} 
          disabled={refreshing || loading || connectionError}
          className="px-4"
        >
          {refreshing ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
              正在刷新...
            </>
          ) : '刷新数据'}
        </Button>
      </div>

      <Row>
        <Col md={6}>
          <Card className="mb-4 shadow-sm">
            <Card.Header className="bg-primary text-white">
              <h2 className="h5 mb-0">当前热搜</h2>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center py-5">
                  <Spinner animation="border" role="status">
                    <span className="visually-hidden">加载中...</span>
                  </Spinner>
                </div>
              ) : connectionError ? (
                <Alert variant="danger">无法连接到后端服务</Alert>
              ) : (
                <div>
                  {Object.entries(hotData).map(([category, items]) => (
                    <div key={category} className="mb-4">
                      <h3 className="h6 border-bottom pb-2 mb-3">{category}</h3>
                      <ListGroup>
                        {renderHotList(items)}
                      </ListGroup>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="mb-4 shadow-sm">
            <Card.Header className="bg-success text-white">
              <h2 className="h5 mb-0">明日预测</h2>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center py-5">
                  <Spinner animation="border" role="status">
                    <span className="visually-hidden">加载中...</span>
                  </Spinner>
                </div>
              ) : connectionError ? (
                <Alert variant="danger">无法连接到后端服务</Alert>
              ) : (
                <Row>
                  {renderPredictions()}
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <footer className="mt-5 pt-3 text-center text-muted border-top">
        <p>&copy; 2025 热搜预测系统 | DeepSeek API 提供支持</p>
      </footer>
    </Container>
  );
}

export default App;
