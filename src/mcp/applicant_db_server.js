#!/usr/bin/env node

/**
 * MCP MySQL Server: ApplicantDB
 * Manages applicant data including profiles, applications, and personal information
 */

const mysql = require('mysql2/promise');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

// Database configuration
const dbConfig = {
  host: process.env.MYSQL_HOST || 'localhost',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || 'Tek@12345',
  database: process.env.MYSQL_DATABASE || 'loan_approval_system',
  port: parseInt(process.env.MYSQL_PORT) || 3306,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

let pool;

// Initialize connection pool
async function initializeDatabase() {
  try {
    pool = mysql.createPool(dbConfig);
    console.error('✅ ApplicantDB connection pool initialized');

    // Verify connection
    const connection = await pool.getConnection();
    await connection.ping();
    connection.release();
    console.error('✅ Database connection verified');
  } catch (error) {
    console.error('❌ Database initialization error:', error.message);
    process.exit(1);
  }
}

// MCP Server instance
const server = new Server({
  name: 'ApplicantDB',
  version: '1.0.0',
});

// List available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'applicant://applicants',
        name: 'All Applicants',
        description: 'Access all applicant records and profiles',
        mimeType: 'application/json'
      },
      {
        uri: 'applicant://applications',
        name: 'Loan Applications',
        description: 'Access all loan applications with status',
        mimeType: 'application/json'
      },
      {
        uri: 'applicant://search',
        name: 'Search Applicants',
        description: 'Search applicants by ID, name, or criteria',
        mimeType: 'application/json'
      }
    ]
  };
});

// Read resources
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  try {
    if (uri === 'applicant://applicants') {
      const connection = await pool.getConnection();
      const [rows] = await connection.query(
        `SELECT * FROM applicants LIMIT 100`
      );
      connection.release();
      return {
        contents: [{
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(rows, null, 2)
        }]
      };
    } else if (uri === 'applicant://applications') {
      const connection = await pool.getConnection();
      const [rows] = await connection.query(
        `SELECT a.*, l.credit_score, l.loan_amount, l.application_status
         FROM applicants a
         LEFT JOIN loan_applications l ON a.applicant_id = l.applicant_id
         LIMIT 100`
      );
      connection.release();
      return {
        contents: [{
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(rows, null, 2)
        }]
      };
    }
  } catch (error) {
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify({ error: error.message })
      }]
    };
  }
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_applicant',
        description: 'Retrieve a single applicant by ID',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: {
              type: 'string',
              description: 'The applicant ID'
            }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'search_applicants',
        description: 'Search applicants by criteria',
        inputSchema: {
          type: 'object',
          properties: {
            criteria: {
              type: 'object',
              description: 'Search criteria (age, income, location, etc.)'
            },
            limit: {
              type: 'integer',
              description: 'Maximum results to return',
              default: 10
            }
          },
          required: ['criteria']
        }
      },
      {
        name: 'get_application_status',
        description: 'Get the status of a loan application',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: {
              type: 'string',
              description: 'The applicant ID'
            }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'get_applicant_profile',
        description: 'Get complete applicant profile including application',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: {
              type: 'string',
              description: 'The applicant ID'
            }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'list_all_applicants',
        description: 'List all applicants with pagination',
        inputSchema: {
          type: 'object',
          properties: {
            page: {
              type: 'integer',
              description: 'Page number',
              default: 1
            },
            limit: {
              type: 'integer',
              description: 'Records per page',
              default: 50
            }
          }
        }
      },
      {
        name: 'get_applicants_by_location',
        description: 'Get all applicants from a specific location',
        inputSchema: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: 'City and state (e.g., "New York, NY")'
            }
          },
          required: ['location']
        }
      },
      {
        name: 'get_applicants_by_employment',
        description: 'Get applicants by employment type',
        inputSchema: {
          type: 'object',
          properties: {
            employment_type: {
              type: 'string',
              enum: ['Salaried', 'Self-Employed', 'Freelancer', 'Business Owner'],
              description: 'Employment type'
            }
          },
          required: ['employment_type']
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const connection = await pool.getConnection();

    switch (name) {
      case 'get_applicant': {
        const [rows] = await connection.query(
          'SELECT * FROM applicants WHERE applicant_id = ?',
          [args.applicant_id]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(rows[0] || { error: 'Applicant not found' })
          }]
        };
      }

      case 'search_applicants': {
        let query = 'SELECT * FROM applicants WHERE 1=1';
        const params = [];

        if (args.criteria.age_min) {
          query += ' AND age >= ?';
          params.push(args.criteria.age_min);
        }
        if (args.criteria.age_max) {
          query += ' AND age <= ?';
          params.push(args.criteria.age_max);
        }
        if (args.criteria.location) {
          query += ' AND location LIKE ?';
          params.push(`%${args.criteria.location}%`);
        }
        if (args.criteria.employment_type) {
          query += ' AND employment_type = ?';
          params.push(args.criteria.employment_type);
        }

        query += ` LIMIT ${args.limit || 10}`;
        const [rows] = await connection.query(query, params);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ count: rows.length, data: rows })
          }]
        };
      }

      case 'get_application_status': {
        const [rows] = await connection.query(
          `SELECT applicant_id, credit_score, loan_amount, application_status, risk_level
           FROM loan_applications WHERE applicant_id = ?`,
          [args.applicant_id]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(rows[0] || { error: 'Application not found' })
          }]
        };
      }

      case 'get_applicant_profile': {
        const [appRows] = await connection.query(
          'SELECT * FROM applicants WHERE applicant_id = ?',
          [args.applicant_id]
        );
        const [loanRows] = await connection.query(
          'SELECT * FROM loan_applications WHERE applicant_id = ?',
          [args.applicant_id]
        );
        const [riskRows] = await connection.query(
          `SELECT income_stability_score, employment_risk_score,
                  credit_category, credit_recommendation, warning_flags
           FROM risk_assessments WHERE applicant_id = ?`,
          [args.applicant_id]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              applicant: appRows[0],
              application: loanRows[0],
              risk_assessment: riskRows[0]
            })
          }]
        };
      }

      case 'list_all_applicants': {
        const page = args.page || 1;
        const limit = args.limit || 50;
        const offset = (page - 1) * limit;

        const [rows] = await connection.query(
          'SELECT * FROM applicants LIMIT ? OFFSET ?',
          [limit, offset]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ page, limit, count: rows.length, data: rows })
          }]
        };
      }

      case 'get_applicants_by_location': {
        const [rows] = await connection.query(
          'SELECT * FROM applicants WHERE location = ? LIMIT 100',
          [args.location]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ location: args.location, count: rows.length, data: rows })
          }]
        };
      }

      case 'get_applicants_by_employment': {
        const [rows] = await connection.query(
          'SELECT * FROM applicants WHERE employment_type = ? LIMIT 100',
          [args.employment_type]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ employment_type: args.employment_type, count: rows.length, data: rows })
          }]
        };
      }

      default:
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ error: `Unknown tool: ${name}` })
          }]
        };
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ error: error.message })
      }]
    };
  } finally {
    connection.release();
  }
});

// Main execution
async function main() {
  await initializeDatabase();

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('✅ ApplicantDB MCP server started and listening for requests');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
