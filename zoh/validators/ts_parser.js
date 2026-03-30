/**
 * ZOH TS Parser Helper
 * Uses @typescript-eslint/typescript-estree to extract API endpoints
 */

const fs = require('fs');
const path = require('path');

async function parseTSFile(filePath) {
    try {
        // Try to require @typescript-eslint/typescript-estree from NODE_PATH
        const { parse } = require('@typescript-eslint/typescript-estree');
        
        const code = fs.readFileSync(filePath, 'utf-8');
        const ast = parse(code, {
            jsx: true,
            loc: true,
            range: true,
        });

        const endpoints = [];

        function walk(node) {
            if (!node) return;

            // Handle Decorators (NestJS style)
            if (node.decorators) {
                node.decorators.forEach(dec => {
                    if (dec.expression && dec.expression.type === 'CallExpression') {
                        const name = dec.expression.callee.name;
                        const methods = ['Get', 'Post', 'Put', 'Delete', 'Patch'];
                        if (methods.includes(name)) {
                            const path = dec.expression.arguments[0]?.value || '/';
                            endpoints.push({
                                method: name.toUpperCase(),
                                path: path,
                                handler: node.id?.name || 'unknown'
                            });
                        }
                    }
                });
            }

            // Handle app.get() / router.post()
            if (node.type === 'CallExpression') {
                const callee = node.callee;
                if (callee.type === 'MemberExpression' && callee.property.type === 'Identifier') {
                    const method = callee.property.name.toLowerCase();
                    const methods = ['get', 'post', 'put', 'delete', 'patch'];
                    if (methods.includes(method)) {
                        const pathArg = node.arguments[0];
                        if (pathArg && pathArg.type === 'Literal') {
                            endpoints.push({
                                method: method.toUpperCase(),
                                path: pathArg.value,
                                handler: 'anonymous'
                            });
                        }
                    }
                }
            }

            // Recursive walk
            for (const key in node) {
                if (node[key] && typeof node[key] === 'object') {
                    if (Array.isArray(node[key])) {
                        node[key].forEach(walk);
                    } else {
                        walk(node[key]);
                    }
                }
            }
        }

        walk(ast);
        console.log(JSON.stringify(endpoints));
    } catch (err) {
        console.error(`Error parsing TS file ${filePath}: ${err.message}`);
        process.exit(1);
    }
}

const targetFile = process.argv[2];
if (targetFile) {
    parseTSFile(targetFile);
} else {
    process.exit(1);
}
