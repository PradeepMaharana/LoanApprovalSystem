#!/usr/bin/env node

/**
 * MCP MySQL Server: NotificationSystem
 * Manages notifications, alerts, and communications for loan decisions
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
    console.error('✅ NotificationSystem connection pool initialized');

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
    // Notifications table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        applicant_id VARCHAR(50) NOT NULL,
        notification_type ENUM('APPLICATION_RECEIVED', 'UNDER_REVIEW', 'APPROVED', 'CONDITIONAL', 'REJECTED', 'DOCUMENTS_NEEDED', 'DECISION_READY') NOT NULL,
        title VARCHAR(255),
        message TEXT NOT NULL,
        status ENUM('PENDING', 'SENT', 'FAILED', 'READ') DEFAULT 'PENDING',
        priority ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM',
        channels JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sent_at TIMESTAMP NULL,
        expires_at TIMESTAMP NULL,
        INDEX idx_applicant (applicant_id),
        INDEX idx_status (status),
        INDEX idx_type (notification_type),
        INDEX idx_created (created_at)
      )
    `);

    // Communication templates table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS communication_templates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        template_name VARCHAR(255) NOT NULL UNIQUE,
        notification_type VARCHAR(100),
        subject_line VARCHAR(255),
        body_template TEXT NOT NULL,
        variables JSON,
        channels JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);

    // Communication history table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS communication_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        applicant_id VARCHAR(50) NOT NULL,
        notification_id INT,
        communication_type ENUM('EMAIL', 'SMS', 'IN_APP', 'LETTER') NOT NULL,
        recipient_address VARCHAR(255),
        subject VARCHAR(255),
        message_content TEXT,
        delivery_status ENUM('PENDING', 'SENT', 'DELIVERED', 'FAILED') DEFAULT 'PENDING',
        delivery_time TIMESTAMP NULL,
        error_message TEXT,
        retry_count INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_applicant (applicant_id),
        INDEX idx_status (delivery_status),
        INDEX idx_created (created_at),
        FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE SET NULL
      )
    `);

    // Alert rules table
    await connection.query(`
      CREATE TABLE IF NOT EXISTS alert_rules (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rule_name VARCHAR(255) NOT NULL UNIQUE,
        trigger_condition TEXT NOT NULL,
        alert_type VARCHAR(100),
        priority ENUM('LOW', 'MEDIUM', 'HIGH'),
        recipients JSON,
        enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);

    console.error('✅ Notification system tables created/verified');

    // Insert default templates
    const [existingTemplates] = await connection.query('SELECT COUNT(*) as count FROM communication_templates');
    if (existingTemplates[0].count === 0) {
      await insertDefaultTemplates(connection);
    }
  } finally {
    connection.release();
  }
}

async function insertDefaultTemplates(connection) {
  const templates = [
    ['Application Received', 'APPLICATION_RECEIVED', 'Your Loan Application Received', 'Dear {applicant_name},\n\nWe have received your loan application (ID: {application_id}). We will review it and contact you within 2-3 business days.\n\nBest regards,\nLoan Team', '["applicant_name", "application_id"]'],
    ['Under Review', 'UNDER_REVIEW', 'Your Application is Under Review', 'Your loan application is currently under review. We may request additional documents if needed.\n\nApplication ID: {application_id}', '["application_id"]'],
    ['Approved', 'APPROVED', 'Your Loan is Approved', 'Congratulations! Your loan application has been approved.\n\nLoan Amount: {loan_amount}\nInterest Rate: {interest_rate}%\nTerm: {loan_term} months', '["loan_amount", "interest_rate", "loan_term"]'],
    ['Documents Needed', 'DOCUMENTS_NEEDED', 'Additional Documents Required', 'To proceed with your application, please submit the following documents:\n\n{required_documents}\n\nApplication ID: {application_id}', '["required_documents", "application_id"]'],
    ['Decision Ready', 'DECISION_READY', 'Your Loan Decision is Ready', 'Your loan application decision is now available. Please log in to view details.\n\nApplication ID: {application_id}', '["application_id"]']
  ];

  for (const [name, type, subject, body, vars] of templates) {
    await connection.query(
      `INSERT IGNORE INTO communication_templates
       (template_name, notification_type, subject_line, body_template, variables, channels)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [name, type, subject, body, vars, JSON.stringify(['EMAIL', 'SMS', 'IN_APP'])]
    );
  }

  console.error('✅ Default communication templates inserted');
}

const server = new Server({
  name: 'NotificationSystem',
  version: '1.0.0',
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'create_notification',
        description: 'Create a new notification for an applicant',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' },
            notification_type: {
              type: 'string',
              enum: ['APPLICATION_RECEIVED', 'UNDER_REVIEW', 'APPROVED', 'CONDITIONAL', 'REJECTED', 'DOCUMENTS_NEEDED', 'DECISION_READY']
            },
            title: { type: 'string' },
            message: { type: 'string' },
            priority: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH'] },
            channels: { type: 'array', items: { type: 'string' } }
          },
          required: ['applicant_id', 'notification_type', 'message']
        }
      },
      {
        name: 'send_notification',
        description: 'Send a pending notification',
        inputSchema: {
          type: 'object',
          properties: {
            notification_id: { type: 'integer' }
          },
          required: ['notification_id']
        }
      },
      {
        name: 'get_notifications',
        description: 'Get notifications for an applicant',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' },
            limit: { type: 'integer', default: 20 }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'get_communication_history',
        description: 'Get communication history for an applicant',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_id: { type: 'string' }
          },
          required: ['applicant_id']
        }
      },
      {
        name: 'get_pending_communications',
        description: 'Get all pending communications across system',
        inputSchema: {
          type: 'object',
          properties: {
            limit: { type: 'integer', default: 50 }
          }
        }
      },
      {
        name: 'mark_notification_read',
        description: 'Mark a notification as read',
        inputSchema: {
          type: 'object',
          properties: {
            notification_id: { type: 'integer' }
          },
          required: ['notification_id']
        }
      },
      {
        name: 'get_communication_templates',
        description: 'Get available communication templates',
        inputSchema: {
          type: 'object',
          properties: {
            notification_type: { type: 'string' }
          }
        }
      },
      {
        name: 'send_bulk_notifications',
        description: 'Send bulk notifications to multiple applicants',
        inputSchema: {
          type: 'object',
          properties: {
            applicant_ids: { type: 'array', items: { type: 'string' } },
            notification_type: { type: 'string' },
            message: { type: 'string' }
          },
          required: ['applicant_ids', 'notification_type', 'message']
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
      case 'create_notification': {
        const [result] = await connection.query(
          `INSERT INTO notifications
           (applicant_id, notification_type, title, message, priority, channels)
           VALUES (?, ?, ?, ?, ?, ?)`,
          [
            args.applicant_id,
            args.notification_type,
            args.title || 'Loan Application Update',
            args.message,
            args.priority || 'MEDIUM',
            JSON.stringify(args.channels || ['EMAIL', 'IN_APP'])
          ]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              notification_id: result.insertId,
              message: 'Notification created successfully'
            })
          }]
        };
      }

      case 'send_notification': {
        await connection.query(
          `UPDATE notifications
           SET status = 'SENT', sent_at = NOW()
           WHERE id = ?`,
          [args.notification_id]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ success: true, notification_id: args.notification_id })
          }]
        };
      }

      case 'get_notifications': {
        const [rows] = await connection.query(
          `SELECT * FROM notifications
           WHERE applicant_id = ?
           ORDER BY created_at DESC
           LIMIT ?`,
          [args.applicant_id, args.limit || 20]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ count: rows.length, notifications: rows })
          }]
        };
      }

      case 'get_communication_history': {
        const [rows] = await connection.query(
          `SELECT * FROM communication_history
           WHERE applicant_id = ?
           ORDER BY created_at DESC`,
          [args.applicant_id]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ count: rows.length, history: rows })
          }]
        };
      }

      case 'get_pending_communications': {
        const [rows] = await connection.query(
          `SELECT * FROM communication_history
           WHERE delivery_status = 'PENDING'
           ORDER BY created_at ASC
           LIMIT ?`,
          [args.limit || 50]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ count: rows.length, pending: rows })
          }]
        };
      }

      case 'mark_notification_read': {
        await connection.query(
          `UPDATE notifications SET status = 'READ' WHERE id = ?`,
          [args.notification_id]
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ success: true, notification_id: args.notification_id })
          }]
        };
      }

      case 'get_communication_templates': {
        let query = 'SELECT * FROM communication_templates';
        if (args.notification_type) {
          query += ' WHERE notification_type = ?';
          const [rows] = await connection.query(query, [args.notification_type]);
          return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
        }
        const [rows] = await connection.query(query);
        return { content: [{ type: 'text', text: JSON.stringify(rows) }] };
      }

      case 'send_bulk_notifications': {
        const results = [];
        for (const appId of args.applicant_ids) {
          const [result] = await connection.query(
            `INSERT INTO notifications
             (applicant_id, notification_type, message, priority)
             VALUES (?, ?, ?, 'MEDIUM')`,
            [appId, args.notification_type, args.message]
          );
          results.push({ applicant_id: appId, notification_id: result.insertId });
        }

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              total_sent: results.length,
              results
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
  console.error('✅ NotificationSystem MCP server started');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
