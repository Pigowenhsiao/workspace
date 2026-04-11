#!/usr/bin/env node
/**
 * sync-to-notion.js
 * Writes a structured note to Notion Input Database
 *
 * Usage:
 *   node sync-to-notion.js "<title>" "<tags_csv>" "<summary>" "<core_points_csv>" "<risks_csv>" "<keypoints_csv>" "<apply>" "<fulltext>" "<source_url>" "<vault_path>"
 *
 * All arguments are required except <fulltext> and <vault_path>
 */

const { Client } = require('/home/pigo/.nvm/versions/node/v22.22.2/lib/node_modules/@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY || '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' });

const DB_ID = '33a42529-badd-80fd-9178-000b0c7998fc';

// Known tags in the Notion database
const KNOWN_TAGS = [
  'AI', 'LLM', 'Claude', 'Codex', 'Agent', 'Prompt', 'Notebooklm',
  'SKILLS', '知識庫', 'Knowledge', 'Tool', 'Video Edit', 'Recipe',
  'cooking', 'investment', 'Vincent', 'AI_Training', 'Gemini', '數位分身', '工作流'
];

// Block helpers
function block(type, text) {
  text = String(text || '').trim();
  if (!text) return null;
  return { object: 'block', type: type, [type]: { rich_text: [{ type: 'text', text: { content: text.slice(0, 1900) } }] } };
}

function h2(text) { return block('heading_2', text); }
function h3(text) { return block('heading_3', text); }
function p(text)  { return block('paragraph', text); }
function bullet(text) { return block('bulleted_list_item', text); }
function divider() { return { object: 'block', type: 'divider', divider: {} }; }

// Split long text into safe chunks
function splitText(text, maxLen) {
  maxLen = maxLen || 1900;
  text = String(text || '');
  if (!text) return [];
  if (text.length <= maxLen) return [text];
  const chunks = [];
  while (text.length > maxLen) {
    let cut = maxLen;
    while (cut > 0 && !' 。，、\n'.includes(text[cut])) cut--;
    if (cut === 0) cut = maxLen;
    chunks.push(text.slice(0, cut));
    text = text.slice(cut).trim();
  }
  if (text) chunks.push(text);
  return chunks;
}

// Parse comma-separated values, treating | as a sub-separator
function parseCsv(csv) {
  if (!csv) return [];
  return csv.split(/[,|]/).map(function(s) { return s.trim(); }).filter(function(s) { return s.length > 0; });
}

// Filter tags against known tags
function filterTags(tags) {
  return tags.filter(function(t) { return KNOWN_TAGS.includes(t); });
}

// Build all blocks for a note
function buildBlocks(args) {
  const b = [];

  // ## 核心摘要
  b.push(h2('核心摘要'));
  splitText(args.summary, 1900).forEach(function(chunk) { b.push(p(chunk)); });

  // ## 文章分析
  b.push(divider());
  b.push(h2('文章分析'));

  // ### 核心論點
  const corePoints = parseCsv(args.core_points);
  if (corePoints.length > 0) {
    b.push(h3('核心論點'));
    corePoints.forEach(function(pt) { b.push(bullet(pt)); });
  }

  // ### 風險與限制
  const risks = parseCsv(args.risks);
  if (risks.length > 0) {
    b.push(h3('風險與限制'));
    risks.forEach(function(r) { b.push(bullet(r)); });
  } else {
    b.push(h3('風險與限制'));
    b.push(bullet('（目前尚無明顯限制或風險）'));
  }

  // ## 關鍵知識點
  b.push(divider());
  b.push(h2('關鍵知識點'));
  const keypoints = parseCsv(args.keypoints);
  if (keypoints.length > 0) {
    keypoints.forEach(function(kp) { b.push(bullet(kp)); });
  } else {
    b.push(bullet('（無）'));
  }

  // ## 我會怎麼用這篇文章
  b.push(divider());
  b.push(h2('我會怎麼用這篇文章'));
  splitText(args.apply, 1900).forEach(function(chunk) { b.push(p(chunk)); });

  // ## 全文（繁中重寫）
  b.push(divider());
  b.push(h2('全文（繁中重寫）'));
  const fulltext = args.fulltext || '（見 Vault 原始檔案）';
  splitText(fulltext, 1900).forEach(function(chunk) { b.push(p(chunk)); });

  // ## Source
  b.push(divider());
  b.push(h2('Source'));
  if (args.source_url) b.push(p(args.source_url));
  if (args.vault_path) b.push(p(args.vault_path));

  return b.filter(function(x) { return x !== null; });
}

// Create a page in Notion
async function createPage(args) {
  const blocks = buildBlocks(args);

  const tags = filterTags(parseCsv(args.tags));
  if (tags.length === 0) tags.push('AI'); // fallback

  const page = await notion.pages.create({
    parent: { data_source_id: DB_ID },
    properties: {
      '名稱': { title: [{ type: 'text', text: { content: args.title || 'Untitled' } }] },
      'Tags': { multi_select: tags.map(function(t) { return { name: t }; }) }
    },
    children: blocks
  });

  return page;
}

// CLI entry
(async function() {
  const args = process.argv.slice(2);

  if (args[0] === '--help' || args[0] === '-h') {
    console.log('Usage: node sync-to-notion.js "<title>" "<tags_csv>" "<summary>" "<core_points_csv>" "<risks_csv>" "<keypoints_csv>" "<apply>" "<fulltext>" "<source_url>" "<vault_path>"');
    process.exit(0);
  }

  if (args.length < 9) {
    console.log('Error: need at least 9 arguments');
    console.log('Usage: node sync-to-notion.js "<title>" "<tags_csv>" "<summary>" "<core_points_csv>" "<risks_csv>" "<keypoints_csv>" "<apply>" "<fulltext>" "<source_url>" "<vault_path>"');
    console.log('Got:', args.length, 'arguments');
    process.exit(1);
  }

  const result = await createPage({
    title: args[0],
    tags: args[1],
    summary: args[2],
    core_points: args[3],
    risks: args[4],
    keypoints: args[5],
    apply: args[6],
    fulltext: args[7],
    source_url: args[8],
    vault_path: args[9] || ''
  });

  console.log('Created:', result.id);
})();
