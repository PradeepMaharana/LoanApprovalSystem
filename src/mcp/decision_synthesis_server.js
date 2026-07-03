#!/usr/bin/env node

/**
 * MCP MySQL Server: DecisionSynthesis
 * Synthesizes loan decisions combining applicant data and risk rules
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
    console.error('✅ DecisionSynthesis connection pool initialized');

    const connection = await pool.getConnection();
    await connection.ping();
    connection.release();

    await createTables();
  } catch (error) {
    console.error('❌ Database initialization error:', error.message);
    process.exit(1);
  }
}

async function createTables() {
  const connection = await pool.getConnection();

  try {
    // Loan decisions table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS loan_decisions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        applicant_id VARCHAR(50) NOT NULL UNIQUE,
        decision_type ENUM('APPROVED', 'CONDITIONAL_APPROVAL', 'REJECTED', 'PENDING_REVIEW') NOT NULL,
        decision_score DECIMAL(5,2),
        decision_date TIMESTAMP,
        decision_rationale TEXT,
        interest_rate DECIMAL(5,2),
        loan_term_months INT,
        conditions TEXT,
        approved_amount DECIMAL(15,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_applicant (applicant_id),
        INDEX idx_decision_type (decision_type),
        INDEX idx_decision_date (decision_date)
      )
    `);

    // Decision justifications table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS decision_justifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        loan_decision_id INT NOT NULL,
        applicant_id VARCHAR(50) NOT NULL,
        factor_name VARCHAR(100),
        factor_value VARCHAR(100),
        risk_assessment TEXT,
        impact_level ENUM('HIGH', 'MEDIUM', 'LOW'),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (loan_decision_id) REFERENCES loan_decisions(id) ON DELETE CASCADE,
        INDEX idx_applicant (applicant_id)
      )
    `);

    // Loan terms table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS loan_terms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        loan_decision_id INT NOT NULL,
        applicant_id VARCHAR(50) NOT NULL,
        principal_amount DECIMAL(15,2),
        interest_rate DECIMAL(5,2),
        term_months INT,
        monthly_payment DECIMAL(10,2),
        total_interest DECIMAL(15,2),
        origination_fee DECIMAL(10,2),
        prepayment_penalty BOOLEAN,
        covenants JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (loan_decision_id) REFERENCES loan_decisions(id) ON DELETE CASCADE,
        INDEX idx_applicant (applicant_id)
      )
    `);

    console.error('✅ Decision synthesis tables created/verified');
  } finally {
    connection.release();
  }
}

const server = new Server({
  name: 'DecisionSynthesis',
  version: '1.0.0',
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'synthesize_loan_decision',
        description: 'Synthesize a complete loan decision for an applicant',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' },
            income_stability_score: { type: 'number' },
            employment_risk_score: { type: 'number' },
            credit_score: { type: 'number' },
            loan_amount: { type: 'number' },
            income: { type: 'number' }
          },
          required: ['applicant_id', 'credit_score', 'loan_amount', 'income']
        }
      },
      {
        name: 'get_loan_decision',
        description: 'Retrieve a saved loan decision',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'get_decision_justification',
        description: 'Get detailed justification for a loan decision',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'calculate_loan_terms',
        description: 'Calculate detailed loan terms based on approved decision',
        inputSchema: {
          type: 'object',
          properties: {
            principal_amount: { type: 'number' },
            interest_rate: { type: 'number' },
            term_months: { type: 'integer' }
          },
          required: ['principal_amount', 'interest_rate', 'term_months']
        }
      },
      {
        name: 'get_all_decisions',
        description: 'Get all loan decisions with optional filtering',
        inputSchema: {
          type: 'object',
          properties: {
            decision_type: {
              type: 'string',
              enum: ['APPROVED', 'CONDITIONAL_APPROVAL', 'REJECTED', 'PENDING_REVIEW']
            },
            limit: { type: 'integer', default: 50 }
          }
        }
      },
      {
        name: 'update_decision_status',
        description: 'Update the status of a loan decision',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' },
            new_status: {
              type: 'string',
              enum: ['APPROVED', 'CONDITIONAL_APPROVAL', 'REJECTED', 'PENDING_REVIEW']
            },
            rationale: { type: 'string' }
          },
          required: ['applicant_id', 'new_status']
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
      case 'synthesize_loan_decision': {
        const creditScore = args.credit_score;
        const dtiRatio = (args.loan_amount) / args.income;
        const incomeStability = args.income_stability_score || 70;
        const employmentRisk = args.employment_risk_score || 50;

        // Calculate overall decision score
        let decisionScore = 100;
        if (creditScore < 650) decisionScore -= 30;
        else if (creditScore < 700) decisionScore -= 15;
        if (dtiRatio > 0.6) decisionScore -= 25;
        else if (dtiRatio > 0.4) decisionScore -= 10;
        decisionScore += (incomeStability - 50) * 0.3;
        decisionScore -= (employmentRisk - 50) * 0.2;

        let decisionType = 'PENDING_REVIEW';
        if (decisionScore >= 75) decisionType = 'APPROVED';
        else if (decisionScore >= 60) decisionType = 'APPROVED';
        else if (decisionScore >= 40) decisionType = 'CONDITIONAL_APPROVAL';
        else decisionType = 'REJECTED';

        let interestRate = 5.5;
        if (creditScore < 650) interestRate += 3;
        else if (creditScore < 700) interestRate += 1.5;
        if (dtiRatio > 0.5) interestRate += 1;

        // Save decision
        const rationale = `Decision synthesized: Credit ${creditScore}, DTI ${dtiRatio.toFixed(2)}, Income Stability ${incomeStability}`;

        await connection.query(
          `INSERT INTO loan_decisions
           (applicant_id, decision_type, decision_score, interest_rate, decision_rationale)
           VALUES (?, ?, ?, ?, ?)
           ON DUPLICATE KEY UPDATE
           decision_type=VALUES(decision_type),
           decision_score=VALUES(decision_score),
           interest_rate=VALUES(interest_rate),
           decision_rationale=VALUES(decision_rationale)`,
          [args.applicant_id, decisionType, decisionScore, interestRate, rationale]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              applicant_id: args.applicant_id,
              decision: decisionType,
              score: decisionScore.toFixed(2),
              interest_rate: interestRate.toFixed(2),
              rationale
            })
          }]
        };
      }

      case 'get_loan_decision': {
        const [rows] = await connection.query(
          'SELECT * FROM loan_decisions WHERE applicant_id = ?',
          [args.applicant_id]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(rows[0] || { error: 'Decision not found' })
          }]
        };
      }

      case 'get_decision_justification': {
        const [rows] = await connection.query(
          'SELECT * FROM decision_justifications WHERE applicant_id = ?',
          [args.applicant_id]
        );
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ count: rows.length, justifications: rows })
          }]
        };
      }

      case 'calculate_loan_terms': {
        const P = args.principal_amount;
        const r = args.interest_rate / 100 / 12;
        const n = args.term_months;

        const monthlyPayment = (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
        const totalPaid = monthlyPayment * n;
        const totalInterest = totalPaid - P;

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              principal: P,
              interest_rate: args.interest_rate,
              term_months: n,
              monthly_payment: monthlyPayment.toFixed(2),
              total_interest: totalInterest.toFixed(2),
              total_paid: totalPaid.toFixed(2)
            })
          }]
        };
      }

      case 'get_all_decisions': {
        let query = 'SELECT * FROM loan_decisions';
        const params = [];

        if (args.decision_type) {
          query += ' WHERE decision_type = ?';
          params.push(args.decision_type);
        }

        query += ' LIMIT ?';
        params.push(args.limit || 50);

        const [rows] = await connection.query(query, params);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ count: rows.length, decisions: rows })
          }]
        };
      }

      case 'update_decision_status': {
        await connection.query(
          `UPDATE loan_decisions
           SET decision_type = ?, decision_rationale = ?, updated_at = NOW()
           WHERE applicant_id = ?`,
          [args.new_status, args.rationale || '', args.applicant_id]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              applicant_id: args.applicant_id,
              new_status: args.new_status,
              success: true
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
  console.error('✅ DecisionSynthesis MCP server started');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
