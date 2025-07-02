import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Stack
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImageIcon from '@mui/icons-material/Image';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import ArticleIcon from '@mui/icons-material/Article';
import { useDropzone } from 'react-dropzone';
import Grid from '@mui/material/Grid';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

const UploadArea = ({ onImageUpload, onGenerateTestCases, isGenerating, uploadedImage, serverStatus = 'checking' }) => {
  const [context, setContext] = useState('');
  const [requirements, setRequirements] = useState('');
  const [inputType, setInputType] = useState('image'); // 'image' 或 'text'
  const [prdText, setPrdText] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onImageUpload(acceptedFiles[0]);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    },
    maxFiles: 1
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputType === 'image') {
      onGenerateTestCases(context, requirements, uploadedImage);
    } else {
      onGenerateTestCases(context, requirements, null, prdText);
    }
  };

  const handleInputTypeChange = (event, newInputType) => {
    if (newInputType !== null) {
      setInputType(newInputType);
    }
  };

  return (
    <Paper 
      elevation={0}
      sx={{ 
        p: { xs: 3, md: 4 }, 
        height: 'fit-content',
        position: 'sticky',
        top: 24
      }}
    >
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          测试用例生成器
        </Typography>
        <Typography variant="body1" color="text.secondary">
          上传流程图或输入PRD文档，AI将为您生成完整的测试用例
        </Typography>
      </Box>
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                选择输入方式
              </Typography>
              <ToggleButtonGroup
                value={inputType}
                exclusive
                onChange={handleInputTypeChange}
                size="medium"
                sx={{ width: '100%' }}
              >
                <ToggleButton 
                  value="image" 
                  sx={{ 
                    flex: 1, 
                    py: 1.5,
                    flexDirection: 'column',
                    gap: 1
                  }}
                >
                  <UploadFileIcon />
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    上传图片
                  </Typography>
                </ToggleButton>
                <ToggleButton 
                  value="text"
                  sx={{ 
                    flex: 1, 
                    py: 1.5,
                    flexDirection: 'column',
                    gap: 1
                  }}
                >
                  <ArticleIcon />
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    输入文本
                  </Typography>
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Grid>

          {inputType === 'image' && (
          <Grid item xs={12}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                上传流程图
              </Typography>
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 3,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  bgcolor: isDragActive ? 'primary.50' : 'grey.50',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'primary.50',
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                <input {...getInputProps()} />
                <Box sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  gap: 2
                }}>
                  <Box sx={{
                    width: 64,
                    height: 64,
                    borderRadius: '50%',
                    bgcolor: 'primary.100',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <CloudUploadIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {isDragActive ? '放开以上传文件' : '拖拽图片到这里'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      或者 <Box component="span" sx={{ color: 'primary.main', fontWeight: 500 }}>点击浏览</Box> 选择文件
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      支持 JPG、PNG、GIF 格式，最大 10MB
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {uploadedImage && (
                <Paper 
                  elevation={0}
                  sx={{ 
                    mt: 3, 
                    p: 3, 
                    border: '1px solid', 
                    borderColor: 'success.200',
                    borderRadius: 2,
                    bgcolor: 'success.50'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <ImageIcon sx={{ color: 'success.main' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {uploadedImage.name}
                    </Typography>
                    <Chip 
                      label={`${(uploadedImage.size / 1024 / 1024).toFixed(2)} MB`} 
                      size="small" 
                      color="success"
                      variant="outlined"
                    />
                  </Box>
                  <Box sx={{ 
                    borderRadius: 2, 
                    overflow: 'hidden',
                    bgcolor: 'white',
                    border: '1px solid',
                    borderColor: 'grey.200'
                  }}>
                    <img
                      src={URL.createObjectURL(uploadedImage)}
                      alt="已上传的图片"
                      style={{ 
                        width: '100%', 
                        maxHeight: '300px', 
                        objectFit: 'contain',
                        display: 'block'
                      }}
                    />
                  </Box>
                </Paper>
              )}
            </Box>
          </Grid>
          )}

          {inputType === 'text' && (
          <Grid item xs={12}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                输入PRD文档
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={10}
                variant="outlined"
                label="产品需求文档内容"
                placeholder="请详细描述产品功能、用户故事、业务流程、交互逻辑等内容...\n\n示例：\n1. 用户登录功能\n- 用户可以通过手机号和密码登录\n- 支持短信验证码登录\n- 登录失败3次后账号锁定30分钟\n\n2. 商品搜索功能\n- 用户可以通过关键词搜索商品\n- 支持按分类、价格、品牌筛选\n- 搜索结果按相关度排序"
                value={prdText}
                onChange={(e) => setPrdText(e.target.value)}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    bgcolor: 'grey.50',
                    '&:hover': {
                      bgcolor: 'white',
                    },
                    '&.Mui-focused': {
                      bgcolor: 'white',
                    }
                  }
                }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                建议输入详细的功能描述，包含用户操作流程和预期结果，以获得更准确的测试用例
              </Typography>
            </Box>
          </Grid>
          )}

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 3 }}>
                测试配置
              </Typography>
              <Stack spacing={3}>
                <TextField
                  label="系统上下文"
                  multiline
                  rows={4}
                  fullWidth
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="请描述被测试系统的背景信息...\n\n例如：\n• 系统类型：Web应用/移动应用/API服务\n• 技术架构：前后端分离/微服务架构\n• 用户群体：C端用户/B端商家/管理员\n• 业务场景：电商交易/内容管理/数据分析"
                  variant="outlined"
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      bgcolor: 'grey.50',
                      '&:hover': {
                        bgcolor: 'white',
                      },
                      '&.Mui-focused': {
                        bgcolor: 'white',
                      }
                    }
                  }}
                />
                <TextField
                  label="测试需求"
                  multiline
                  rows={4}
                  fullWidth
                  value={requirements}
                  onChange={(e) => setRequirements(e.target.value)}
                  placeholder="请描述测试用例生成的具体要求...\n\n例如：\n• 测试类型：功能测试/接口测试/UI测试\n• 覆盖范围：正常流程/异常流程/边界条件\n• 测试深度：冒烟测试/回归测试/全量测试\n• 特殊要求：性能指标/安全验证/兼容性"
                  variant="outlined"
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      bgcolor: 'grey.50',
                      '&:hover': {
                        bgcolor: 'white',
                      },
                      '&.Mui-focused': {
                        bgcolor: 'white',
                      }
                    }
                  }}
                />
              </Stack>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              disabled={
                isGenerating || 
                !context || 
                !requirements || 
                serverStatus !== 'connected' ||
                (inputType === 'image' && !uploadedImage) ||
                (inputType === 'text' && !prdText.trim())
              }
              sx={{
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 2,
                textTransform: 'none',
                boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
                '&:hover': {
                  boxShadow: '0 6px 16px rgba(25, 118, 210, 0.4)',
                  transform: 'translateY(-1px)',
                },
                '&:disabled': {
                  bgcolor: 'grey.300',
                  color: 'grey.500',
                  boxShadow: 'none',
                },
                transition: 'all 0.2s ease'
              }}
            >
              {isGenerating ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} color="inherit" />
                  <Typography variant="inherit">AI正在生成测试用例...</Typography>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <UploadFileIcon />
                  <Typography variant="inherit">开始生成测试用例</Typography>
                </Box>
              )}
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default UploadArea;
