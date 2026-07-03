#!/usr/bin/env node

/**
 * MCP MySQL Server: RiskRulesDB
 * Manages risk assessment rules, algorithms, and decision thresholds
 */

const mysql = require('mysql2/promise');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

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

async function initializeDatabase() {
  try {
    pool = mysql.createPool(dbConfig);
    console.error('✅ RiskRulesDB connection pool initialized');

    const connection = await pool.getConnection();
    await connection.ping();
    connection.release();
    console.error('✅ Database connection verified');

    // Create tables if they don't exist
    await createTables();
  } catch (error) {
    console.error('❌ Database initialization error:', error.message);
    process.exit(1);
  }
}

async function createTables() {
  const connection = await pool.getConnection();

  try {
    // Risk thresholds table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS risk_thresholds (
        id INT AUTO_INCREMENT PRIMARY KEY,
        risk_factor VARCHAR(100) UNIQUE NOT NULL,
        min_threshold DECIMAL(5,2),
        max_threshold DECIMAL(5,2),
        impact_on_approval INT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);

    // Risk rules table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS risk_rules (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rule_name VARCHAR(255) NOT NULL,
        rule_type ENUM('income_stability', 'employment_risk', 'credit_history', 'debt_ratio') NOT NULL,
        condition TEXT NOT NULL,
        action VARCHAR(100) NOT NULL,
        priority INT DEFAULT 0,
        enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);

    // Decision rules table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS decision_rules (
        id INT AUTO_INCREMENT PRIMARY KEY,
        decision_type VARCHAR(100) NOT NULL,
        risk_score_min DECIMAL(5,2),
        risk_score_max DECIMAL(5,2),
        recommendation VARCHAR(100),
        interest_rate_adjustment DECIMAL(5,2),
        loan_term_adjustment INT,
        collateral_required BOOLEAN,
        covenants TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);

    // Scoring algorithms table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS scoring_algorithms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        algorithm_name VARCHAR(255) NOT NULL UNIQUE,
        algorithm_type ENUM('income_stability', 'employment_risk', 'credit_score', 'combined') NOT NULL,
        formula TEXT NOT NULL,
        weights JSON,
        description TEXT,
        version VARCHAR(20),
        enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);

    console.error('✅ Risk rules tables created/verified');

    // Insert default rules if empty
    const [existingRules] = await connection.query('SELECT COUNT(*) as count FROM risk_thresholds');
    if (existingRules[0].count === 0) {
      await insertDefaultRules(connection);
    }
  } finally {
    connection.release();
  }
}

async function insertDefaultRules(connection) {
  const defaultThresholds = [
    ['credit_score', 300, 850, 40, 'FICO credit score range'],
    ['dti_ratio', 0, 1, 30, 'Debt-to-income ratio'],
    ['income_stability', 0, 100, 30, 'Income stability score'],
    ['employment_risk', 0, 100, 25, 'Employment risk score'],
    ['loan_to_value', 0, 10, 20, 'Loan to income ratio'],
    ['age', 18, 100, 15, 'Applicant age']
  ];

  for (const [factor, min, max, impact, desc] of defaultThresholds) {
    await connection.query(
      'INSERT IGNORE INTO risk_thresholds (risk_factor, min_threshold, max_threshold, impact_on_approval, description) VALUES (?, ?, ?, ?, ?)',
      [factor, min, max, impact, desc]
    );
  }

  console.error('✅ Default risk thresholds inserted');
}

const server = new Server({
  name: 'RiskRulesDB',
  version: '1.0.0',
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_risk_thresholds',
        description: 'Get all risk assessment thresholds',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'get_threshold_by_factor',
        description: 'Get threshold for a specific risk factor',
        inputSchema: {
          type: 'object',
          properties: {
            risk_factor: {
              type: 'string',
              description: 'Risk factor name'
            }
          },
          required: ['risk_factor']
        }
      },
      {
        name: 'get_risk_rules',
        description: 'Get all active risk assessment rules',
        inputSchema: {
          type: 'object',
          properties: {
            rule_type: {
              type: 'string',
              enum: ['income_stability', 'employment_risk', 'credit_history', 'debt_ratio'],
              description: 'Filter by rule type'
            }
          }
        }
      },
      {
        name: 'get_decision_rules',
        description: 'Get loan decision rules by risk score range',
        inputSchema: {
          type: 'object',
          properties: {
            risk_score: {
              type: 'number',
              description: 'Risk score to find matching rules'
            }
          },
          required: ['risk_score']
        }
      },
      {
        name: 'get_scoring_algorithms',
        description: 'Get available scoring algorithms',
        inputSchema: {
          type: 'object',
          properties: {
            algorithm_type: {
              type: 'string',
              enum: ['income_stability', 'employment_risk', 'credit_score', 'combined'],
              description: 'Filter by algorithm type'
            }
          }
        }
      },
      {
        name: 'evaluate_risk_rules',
        description: 'Evaluate how applicant data matches risk rules',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_data: {
              type: 'object',
              description: 'Applicant data to evaluate'
            }
          },
          required: ['applicant_data']
        }
      },
      {
        name: 'get_recommendation_for_score',
        description: 'Get loan recommendation based on risk score',
        inputSchema: {
          type: 'object',
          properties: {
            risk_score: {
              type: 'number',
              description: 'Risk score between 0-100'
            }
          },
          required: ['risk_score']
        }
      }
    ]
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const connection = await pool.getConnection();

    switch (name) {
      case 'get_risk_thresholds': {
        const [rows] = await connection.query('SELECT * FROM risk_thresholds');
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(rows)
          }]
        };
      }

      case 'get_threshold_by_factor': {
        const [rows] = await connection.query(
          'SELECT * FROM risk_thresholds WHERE risk_factor = ?',
          [args.risk_factor]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(rows[0] || { error: 'Threshold not found' })
          }]
        };
      }

      case 'get_risk_rules': {
        let query = 'SELECT * FROM risk_rules WHERE enabled = TRUE';
        if (args.rule_type) {
          query += ' AND rule_type = ?';
          const [rows] = await connection.query(query, [args.rule_type]);
          return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
        }
        const [rows] = await connection.query(query);
        return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
      }

      case 'get_decision_rules': {
        const [rows] = await connection.query(
          `SELECT * FROM decision_rules
           WHERE risk_score_min <= ? AND risk_score_max >= ?`,
          [args.risk_score, args.risk_score]
        );
        return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
      }

      case 'get_scoring_algorithms': {
        let query = 'SELECT * FROM scoring_algorithms WHERE enabled = TRUE';
        if (args.algorithm_type) {
          query += ' AND algorithm_type = ?';
          const [rows] = await connection.query(query, [args.algorithm_type]);
          return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
        }
        const [rows] = await connection.query(query);
        return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
      }

      case 'get_recommendation_for_score': {
        const score = args.risk_score;
        let recommendation = 'REVIEW_REQUIRED';
        let interestAdjustment = 0;

        if (score >= 75) {
          recommendation = 'STRONG_APPROVAL';
          interestAdjustment = -2;
        } else if (score >= 60) {
          recommendation = 'APPROVAL';
          interestAdjustment = 0;
        } else if (score >= 40) {
          recommendation = 'CONDITIONAL_APPROVAL';
          interestAdjustment = 2;
        } else if (score >= 20) {
          recommendation = 'FURTHER_REVIEW';
          interestAdjustment = 4;
        } else {
          recommendation = 'REJECTION';
          interestAdjustment = 0;
        }

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              risk_score: score,
              recommendation,
              interest_rate_adjustment: interestAdjustment,
              description: `Recommendation based on risk score: ${score}`
            })
          }]
        };
      }

      default:
        return { content: [{ type: 'text', text: JSON.stringify({ error: `Unknown tool: ${name}` }) }] };
    }
  } catch (error) {
    return { content: [{ type: 'text', text: JSON.stringify({ error: error.message }) }] };
  } finally {
    connection.release();
  }
});

async function main() {
  await initializeDatabase();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('✅ RiskRulesDB MCP server started');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
