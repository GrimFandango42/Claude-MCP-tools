#!/usr/bin/env node

/**
 * N8n Workflow Generator MCP Server
 * 
 * A Model Context Protocol server that provides N8n workflow generation
 * and management capabilities.
 * 
 * Features:
 * - Generate N8n workflows from natural language descriptions
 * - Validate workflow JSON structure
 * - Create common workflow templates
 * - Add and connect nodes
 * - Export workflows for N8n import
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Server instance
const server = new Server(
  {
    name: 'n8n-mcp-server',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Structured logging to stderr
function log(level, message, meta = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    server: 'n8n-mcp-server',
    ...meta
  };
  console.error(JSON.stringify(logEntry));
}

const logger = {
  info: (message, meta) => log('info', message, meta),
  error: (message, meta) => log('error', message, meta),
  warn: (message, meta) => log('warn', message, meta),
  debug: (message, meta) => log('debug', message, meta)
};

// N8n Node Templates
const NODE_TEMPLATES = {
  'Manual Trigger': {
    id: '',
    name: 'Manual Trigger',
    type: 'n8n-nodes-base.manualTrigger',
    typeVersion: 1,
    position: [240, 300],
    parameters: {},
    webhookId: ''
  },
  'HTTP Request': {
    id: '',
    name: 'HTTP Request',
    type: 'n8n-nodes-base.httpRequest',
    typeVersion: 4.2,
    position: [460, 300],
    parameters: {
      url: '',
      options: {}
    }
  },
  'Code': {
    id: '',
    name: 'Code',
    type: 'n8n-nodes-base.code',
    typeVersion: 2,
    position: [680, 300],
    parameters: {
      jsCode: '// Add your JavaScript code here\nreturn $input.all();'
    }
  },
  'Set': {
    id: '',
    name: 'Set',
    type: 'n8n-nodes-base.set',
    typeVersion: 3.4,
    position: [900, 300],
    parameters: {
      assignments: {
        assignments: []
      },
      options: {}
    }
  },
  'IF': {
    id: '',
    name: 'IF',
    type: 'n8n-nodes-base.if',
    typeVersion: 2,
    position: [1120, 300],
    parameters: {
      conditions: {
        options: {
          caseSensitive: true,
          leftValue: '',
          typeValidation: 'strict'
        },
        conditions: []
      }
    }
  },
  'Schedule Trigger': {
    id: '',
    name: 'Schedule Trigger',
    type: 'n8n-nodes-base.scheduleTrigger',
    typeVersion: 1.2,
    position: [240, 300],
    parameters: {
      rule: {
        interval: [
          {
            field: 'cronExpression',
            expression: '0 9 * * 1-5'
          }
        ]
      }
    }
  },
  'Webhook': {
    id: '',
    name: 'Webhook',
    type: 'n8n-nodes-base.webhook',
    typeVersion: 2,
    position: [240, 300],
    parameters: {
      path: '',
      options: {}
    },
    webhookId: ''
  },
  'Gmail': {
    id: '',
    name: 'Gmail',
    type: 'n8n-nodes-base.gmail',
    typeVersion: 2.1,
    position: [460, 300],
    parameters: {
      operation: 'send',
      resource: 'message'
    }
  },
  'Slack': {
    id: '',
    name: 'Slack',
    type: 'n8n-nodes-base.slack',
    typeVersion: 2.2,
    position: [460, 300],
    parameters: {
      operation: 'postMessage',
      resource: 'message'
    }
  },
  'Google Sheets': {
    id: '',
    name: 'Google Sheets',
    type: 'n8n-nodes-base.googleSheets',
    typeVersion: 4.4,
    position: [460, 300],
    parameters: {
      operation: 'append',
      resource: 'spreadsheet'
    }
  }
};

// Common workflow templates
const WORKFLOW_TEMPLATES = {
  'basic-http-processing': {
    name: 'Basic HTTP Data Processing',
    description: 'Simple workflow that fetches data via HTTP and processes it',
    nodes: ['Manual Trigger', 'HTTP Request', 'Code', 'Set'],
    connections: [
      { from: 0, to: 1 },
      { from: 1, to: 2 },
      { from: 2, to: 3 }
    ]
  },
  'scheduled-data-sync': {
    name: 'Scheduled Data Synchronization',
    description: 'Workflow that runs on a schedule to sync data between systems',
    nodes: ['Schedule Trigger', 'HTTP Request', 'IF', 'Google Sheets'],
    connections: [
      { from: 0, to: 1 },
      { from: 1, to: 2 },
      { from: 2, to: 3, outputIndex: 0 }
    ]
  },
  'webhook-notification': {
    name: 'Webhook to Notification',
    description: 'Receive webhook data and send notifications via Slack/Gmail',
    nodes: ['Webhook', 'Code', 'IF', 'Slack', 'Gmail'],
    connections: [
      { from: 0, to: 1 },
      { from: 1, to: 2 },
      { from: 2, to: 3, outputIndex: 0 },
      { from: 2, to: 4, outputIndex: 1 }
    ]
  }
};

// Helper functions
function generateNodeId() {
  return uuidv4();
}

function createNode(nodeType, customParams = {}, position = null) {
  const template = NODE_TEMPLATES[nodeType];
  if (!template) {
    throw new Error(`Unknown node type: ${nodeType}`);
  }

  const node = {
    ...JSON.parse(JSON.stringify(template)), // Deep clone
    id: generateNodeId(),
    ...customParams
  };

  if (position) {
    node.position = position;
  }

  if (node.webhookId !== undefined) {
    node.webhookId = generateNodeId();
  }

  return node;
}

function createConnection(sourceNodeIndex, targetNodeIndex, outputIndex = 0, inputIndex = 0) {
  return {
    [sourceNodeIndex]: {
      main: [
        [
          {
            node: targetNodeIndex,
            type: 'main',
            index: inputIndex
          }
        ]
      ]
    }
  };
}

function generateWorkflow(name, description, nodes, connections = []) {
  const workflowNodes = nodes.map((nodeConfig, index) => {
    let nodeType, customParams = {};
    
    if (typeof nodeConfig === 'string') {
      nodeType = nodeConfig;
    } else {
      nodeType = nodeConfig.type;
      customParams = nodeConfig.params || {};
    }

    const position = [240 + (index * 220), 300];
    return createNode(nodeType, customParams, position);
  });

  // Generate connections
  const workflowConnections = {};
  connections.forEach(conn => {
    const sourceIndex = conn.from;
    const targetIndex = conn.to;
    const outputIndex = conn.outputIndex || 0;
    const inputIndex = conn.inputIndex || 0;

    if (!workflowConnections[sourceIndex]) {
      workflowConnections[sourceIndex] = { main: [] };
    }
    
    while (workflowConnections[sourceIndex].main.length <= outputIndex) {
      workflowConnections[sourceIndex].main.push([]);
    }

    workflowConnections[sourceIndex].main[outputIndex].push({
      node: targetIndex,
      type: 'main',
      index: inputIndex
    });
  });

  return {
    name: name,
    nodes: workflowNodes,
    connections: workflowConnections,
    active: false,
    settings: {
      executionOrder: 'v1'
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    id: generateNodeId(),
    tags: []
  };
}

function validateWorkflow(workflow) {
  const errors = [];

  // Basic structure validation
  if (!workflow.name || typeof workflow.name !== 'string') {
    errors.push('Workflow must have a valid name');
  }

  if (!Array.isArray(workflow.nodes)) {
    errors.push('Workflow must have a nodes array');
  } else {
    // Validate each node
    workflow.nodes.forEach((node, index) => {
      if (!node.id || typeof node.id !== 'string') {
        errors.push(`Node ${index} must have a valid id`);
      }
      if (!node.type || typeof node.type !== 'string') {
        errors.push(`Node ${index} must have a valid type`);
      }
      if (!Array.isArray(node.position) || node.position.length !== 2) {
        errors.push(`Node ${index} must have a valid position array [x, y]`);
      }
    });
  }

  if (workflow.connections && typeof workflow.connections !== 'object') {
    errors.push('Connections must be an object');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

// MCP Tool Handlers

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'generate_workflow',
        description: 'Generate an N8n workflow from a natural language description',
        inputSchema: {
          type: 'object',
          properties: {
            description: {
              type: 'string',
              description: 'Natural language description of the desired workflow'
            },
            name: {
              type: 'string',
              description: 'Name for the workflow (optional)'
            },
            template: {
              type: 'string',
              description: 'Base template to use (optional)',
              enum: Object.keys(WORKFLOW_TEMPLATES)
            }
          },
          required: ['description']
        }
      },
      {
        name: 'create_template',
        description: 'Create a workflow from a predefined template',
        inputSchema: {
          type: 'object',
          properties: {
            template: {
              type: 'string',
              description: 'Template name',
              enum: Object.keys(WORKFLOW_TEMPLATES)
            },
            name: {
              type: 'string',
              description: 'Custom name for the workflow (optional)'
            },
            customizations: {
              type: 'object',
              description: 'Custom parameters for nodes (optional)'
            }
          },
          required: ['template']
        }
      },
      {
        name: 'validate_workflow',
        description: 'Validate an N8n workflow JSON structure',
        inputSchema: {
          type: 'object',
          properties: {
            workflow: {
              type: 'object',
              description: 'N8n workflow JSON to validate'
            }
          },
          required: ['workflow']
        }
      },
      {
        name: 'list_node_types',
        description: 'List available N8n node types and templates',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'create_custom_workflow',
        description: 'Create a custom workflow with specific nodes and connections',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Workflow name'
            },
            description: {
              type: 'string',
              description: 'Workflow description'
            },
            nodes: {
              type: 'array',
              description: 'Array of node configurations',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  params: { type: 'object' }
                }
              }
            },
            connections: {
              type: 'array',
              description: 'Array of connection configurations',
              items: {
                type: 'object',
                properties: {
                  from: { type: 'number' },
                  to: { type: 'number' },
                  outputIndex: { type: 'number' },
                  inputIndex: { type: 'number' }
                }
              }
            }
          },
          required: ['name', 'nodes']
        }
      },
      {
        name: 'export_workflow',
        description: 'Export workflow in N8n import format',
        inputSchema: {
          type: 'object',
          properties: {
            workflow: {
              type: 'object',
              description: 'Workflow to export'
            },
            format: {
              type: 'string',
              description: 'Export format',
              enum: ['json', 'clipboard'],
              default: 'json'
            }
          },
          required: ['workflow']
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'generate_workflow': {
        const { description, name: workflowName, template } = args;
        
        logger.info('Generating workflow', { description, workflowName, template });

        // Simple workflow generation based on description keywords
        let nodes = ['Manual Trigger'];
        let connections = [];

        // Analyze description for common patterns
        const lowerDesc = description.toLowerCase();
        
        if (lowerDesc.includes('http') || lowerDesc.includes('api') || lowerDesc.includes('fetch')) {
          nodes.push('HTTP Request');
        }
        
        if (lowerDesc.includes('process') || lowerDesc.includes('transform') || lowerDesc.includes('code')) {
          nodes.push('Code');
        }
        
        if (lowerDesc.includes('set') || lowerDesc.includes('variable') || lowerDesc.includes('assign')) {
          nodes.push('Set');
        }
        
        if (lowerDesc.includes('condition') || lowerDesc.includes('if') || lowerDesc.includes('check')) {
          nodes.push('IF');
        }
        
        if (lowerDesc.includes('slack')) {
          nodes.push('Slack');
        }
        
        if (lowerDesc.includes('gmail') || lowerDesc.includes('email')) {
          nodes.push('Gmail');
        }
        
        if (lowerDesc.includes('sheet') || lowerDesc.includes('spreadsheet')) {
          nodes.push('Google Sheets');
        }

        // Create linear connections between nodes
        for (let i = 0; i < nodes.length - 1; i++) {
          connections.push({ from: i, to: i + 1 });
        }

        const workflow = generateWorkflow(
          workflowName || 'Generated Workflow',
          description,
          nodes,
          connections
        );

        return {
          content: [
            {
              type: 'text',
              text: `Generated N8n workflow "${workflow.name}" with ${nodes.length} nodes.\n\nWorkflow JSON:\n\`\`\`json\n${JSON.stringify(workflow, null, 2)}\n\`\`\``
            }
          ]
        };
      }

      case 'create_template': {
        const { template, name: customName, customizations = {} } = args;
        
        if (!WORKFLOW_TEMPLATES[template]) {
          throw new McpError(ErrorCode.InvalidParams, `Unknown template: ${template}`);
        }

        logger.info('Creating workflow from template', { template, customName });

        const templateConfig = WORKFLOW_TEMPLATES[template];
        const workflow = generateWorkflow(
          customName || templateConfig.name,
          templateConfig.description,
          templateConfig.nodes,
          templateConfig.connections
        );

        return {
          content: [
            {
              type: 'text',
              text: `Created workflow from template "${template}".\n\nWorkflow JSON:\n\`\`\`json\n${JSON.stringify(workflow, null, 2)}\n\`\`\``
            }
          ]
        };
      }

      case 'validate_workflow': {
        const { workflow } = args;
        
        logger.info('Validating workflow');

        const validation = validateWorkflow(workflow);

        return {
          content: [
            {
              type: 'text',
              text: `Workflow validation ${validation.valid ? 'PASSED' : 'FAILED'}\n\n${
                validation.valid 
                  ? 'The workflow structure is valid and ready for N8n import.'
                  : 'Validation errors:\n' + validation.errors.map(err => `- ${err}`).join('\n')
              }`
            }
          ]
        };
      }

      case 'list_node_types': {
        logger.info('Listing available node types');

        const nodeTypes = Object.keys(NODE_TEMPLATES);
        const templates = Object.keys(WORKFLOW_TEMPLATES);

        return {
          content: [
            {
              type: 'text',
              text: `Available N8n Node Types:\n${nodeTypes.map(type => `- ${type}`).join('\n')}\n\nWorkflow Templates:\n${templates.map(template => {
                const config = WORKFLOW_TEMPLATES[template];
                return `- **${template}**: ${config.description}`;
              }).join('\n')}`
            }
          ]
        };
      }

      case 'create_custom_workflow': {
        const { name: workflowName, description = '', nodes, connections = [] } = args;
        
        logger.info('Creating custom workflow', { workflowName, nodeCount: nodes.length });

        const workflow = generateWorkflow(workflowName, description, nodes, connections);

        return {
          content: [
            {
              type: 'text',
              text: `Created custom workflow "${workflowName}" with ${nodes.length} nodes.\n\nWorkflow JSON:\n\`\`\`json\n${JSON.stringify(workflow, null, 2)}\n\`\`\``
            }
          ]
        };
      }

      case 'export_workflow': {
        const { workflow, format = 'json' } = args;
        
        logger.info('Exporting workflow', { format });

        const validation = validateWorkflow(workflow);
        if (!validation.valid) {
          throw new McpError(ErrorCode.InvalidParams, `Invalid workflow: ${validation.errors.join(', ')}`);
        }

        const exportData = {
          name: workflow.name,
          nodes: workflow.nodes,
          connections: workflow.connections,
          active: workflow.active || false,
          settings: workflow.settings || { executionOrder: 'v1' },
          createdAt: workflow.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          id: workflow.id || generateNodeId(),
          tags: workflow.tags || []
        };

        return {
          content: [
            {
              type: 'text',
              text: `Exported workflow "${workflow.name}" in ${format} format.\n\n**Ready for N8n Import:**\n\`\`\`json\n${JSON.stringify(exportData, null, 2)}\n\`\`\`\n\n**Instructions:**\n1. Copy the JSON above\n2. Open N8n\n3. Click "Import from JSON"\n4. Paste the JSON\n5. Configure any required credentials`
            }
          ]
        };
      }

      default:
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    }
  } catch (error) {
    logger.error('Tool execution error', { tool: name, error: error.message, stack: error.stack });
    
    if (error instanceof McpError) {
      throw error;
    }
    
    throw new McpError(ErrorCode.InternalError, `Tool execution failed: ${error.message}`);
  }
});

// Error handling
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', { error: error.message, stack: error.stack });
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection', { reason, promise });
  process.exit(1);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  logger.info('N8n MCP Server started');
}

main().catch((error) => {
  logger.error('Failed to start server', { error: error.message, stack: error.stack });
  process.exit(1);
});
