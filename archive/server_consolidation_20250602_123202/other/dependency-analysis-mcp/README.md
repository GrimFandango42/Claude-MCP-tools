# Dependency Analysis MCP Server

Comprehensive dependency analysis and security scanning server for Claude Desktop, providing vulnerability detection, license compliance, and dependency management.

## Features

### Security Vulnerability Scanning
- **Multi-Tool Integration**: pip-audit, safety, npm audit
- **CVE Tracking**: Common Vulnerabilities and Exposures identification
- **Severity Assessment**: Critical, high, medium, low risk categorization
- **Fix Recommendations**: Automated upgrade suggestions with version targeting
- **Advisory Links**: Direct links to security advisories and patches

### License Compliance Management
- **License Detection**: Automatic license identification for all dependencies
- **Compatibility Analysis**: Assess license compatibility with project requirements
- **Risk Scoring**: Quantitative risk assessment for license combinations
- **Compliance Reporting**: Detailed reports for legal and compliance review
- **Policy Enforcement**: Configurable allowed/blocked license lists

### Dependency Health Analysis
- **Update Availability**: Track outdated packages with version comparison
- **Risk Assessment**: Evaluate update safety (major/minor/patch classification)
- **Unused Detection**: Identify dependencies not actively used in codebase
- **Version Conflicts**: Detect and resolve dependency version conflicts
- **Maintenance Scoring**: Overall project dependency health metrics

### Multi-Language Support
- **Python**: pip-audit, safety, requirements.txt analysis
- **JavaScript/Node.js**: npm audit, package.json analysis
- **Language Detection**: Automatic project language identification
- **Extensible Architecture**: Framework for adding additional languages

## Tools

### `scan_vulnerabilities`
Comprehensive security vulnerability scanning.

```json
{
  "project_path": "/path/to/project",
  "language": "python"
}
```

### `check_licenses`
License compliance analysis and validation.

```json
{
  "project_path": "/path/to/project",
  "allowed_licenses": ["MIT", "Apache-2.0", "BSD-3-Clause"]
}
```

### `find_unused_dependencies`
Identify dependencies not actively used in code.

```json
{
  "project_path": "/path/to/project",
  "language": "auto"
}
```

### `analyze_version_conflicts`
Detect and analyze version compatibility issues.

```json
{
  "project_path": "/path/to/project",
  "language": "python"
}
```

### `suggest_updates`
Smart update recommendations based on risk tolerance.

```json
{
  "project_path": "/path/to/project",
  "risk_level": "medium"
}
```

### `comprehensive_dependency_analysis`
Complete dependency health assessment.

```json
{
  "project_path": "/path/to/project",
  "language": "auto"
}
```

## Installation

```bash
cd servers/dependency-analysis-mcp
pip install -e .
```

### Required Security Tools

Install the security scanning tools:
```bash
# Python security tools
pip install pip-audit safety

# JavaScript security tools (if using Node.js projects)
npm install -g npm
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dependency-analysis": {
      "command": "python",
      "args": ["servers/dependency-analysis-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Usage Examples

### Security Assessment
```
Scan my project for security vulnerabilities and prioritize fixes by severity level.
```

### License Compliance Check
```
Check if all my project dependencies are compatible with MIT license and identify any problematic licenses.
```

### Dependency Cleanup
```
Find unused dependencies in my project and suggest which ones can be safely removed.
```

### Safe Update Strategy
```
Suggest dependency updates with low to medium risk that include security fixes.
```

### Complete Health Check
```
Perform a comprehensive dependency analysis covering security, licenses, updates, and unused packages.
```

## Security Analysis Features

### Vulnerability Detection
- **CVE Database**: Integration with Common Vulnerabilities and Exposures
- **Advisory Tracking**: Links to security advisories and fix documentation
- **Severity Scoring**: CVSS-based severity assessment
- **Affected Versions**: Precise version range identification
- **Fix Availability**: Immediate identification of patched versions

### Risk Assessment Matrix
```python
{
  "critical": {
    "score_impact": -50,
    "action_required": "immediate",
    "max_acceptable": 0
  },
  "high": {
    "score_impact": -20,
    "action_required": "urgent",
    "max_acceptable": 2
  },
  "medium": {
    "score_impact": -10,
    "action_required": "planned",
    "max_acceptable": 5
  },
  "low": {
    "score_impact": -2,
    "action_required": "optional",
    "max_acceptable": 10
  }
}
```

## License Compliance Engine

### License Categories
- **Permissive**: MIT, Apache, BSD (High compatibility score)
- **Copyleft**: GPL, LGPL (Medium compatibility, disclosure requirements)
- **Proprietary**: Commercial licenses (Low compatibility, usage restrictions)
- **Unknown**: Unidentified licenses (Zero compatibility, requires review)

### Compliance Scoring
```python
compatibility_score = (
    (permissive_count * 100) +
    (copyleft_count * 60) +
    (proprietary_count * 30) +
    (unknown_count * 0)
) / total_dependencies
```

### Risk Factors
- **License Conflicts**: Incompatible license combinations
- **Copyleft Obligations**: Source disclosure requirements
- **Commercial Restrictions**: Usage limitation clauses
- **Attribution Requirements**: Credit and notice obligations

## Update Management

### Update Classification
- **Patch Updates** (1.0.0 → 1.0.1): Low risk, bug fixes
- **Minor Updates** (1.0.0 → 1.1.0): Medium risk, new features
- **Major Updates** (1.0.0 → 2.0.0): High risk, breaking changes

### Risk Assessment Criteria
```python
def assess_update_risk(current_version, target_version, package_name):
    risk_factors = {
        "version_jump": calculate_version_distance(),
        "package_popularity": get_package_download_stats(),
        "breaking_changes": analyze_changelog(),
        "security_fixes": check_security_patches(),
        "dependency_impact": analyze_downstream_effects()
    }
    return weighted_risk_score(risk_factors)
```

## Integration Patterns

### With Code Analysis MCP
```python
# Security-aware code analysis
1. dependency_analysis.scan_vulnerabilities("/project")
2. code_analysis.analyze_code_structure(vulnerable_files)
3. dependency_analysis.suggest_updates(risk_level="low")
```

### With Code Quality MCP
```python
# Quality-driven dependency management
1. dependency_analysis.find_unused_dependencies("/project")
2. code_quality.lint_code(affected_files, auto_fix=True)
3. dependency_analysis.analyze_version_conflicts("/project")
```

### With CI/CD Integration
```python
# Automated security pipeline
1. dependency_analysis.comprehensive_dependency_analysis("/project")
2. Fail build if critical vulnerabilities detected
3. Generate security report for review
4. Auto-create PRs for safe updates
```

## Reporting and Dashboards

### Security Score Calculation
```python
security_score = max(0, 100 - (
    (critical_vulns * 50) +
    (high_vulns * 20) +
    (medium_vulns * 10) +
    (low_vulns * 2)
))
```

### Maintenance Score
```python
maintenance_score = max(0, 100 - (
    (outdated_packages * 3) +
    (major_updates_needed * 10) +
    (unused_dependencies * 5)
))
```

### Compliance Dashboard
- **License Distribution**: Visual breakdown of license types
- **Risk Heat Map**: Color-coded risk assessment grid
- **Trend Analysis**: Historical dependency health tracking
- **Action Items**: Prioritized remediation tasks

## Advanced Configuration

### Custom License Policies
```json
{
  "license_policy": {
    "allowed": ["MIT", "Apache-2.0", "BSD-3-Clause"],
    "restricted": ["GPL-3.0", "AGPL-3.0"],
    "review_required": ["LGPL-2.1", "MPL-2.0"],
    "forbidden": ["Proprietary", "Unknown"]
  }
}
```

### Security Thresholds
```json
{
  "security_policy": {
    "max_critical_vulnerabilities": 0,
    "max_high_vulnerabilities": 2,
    "max_total_vulnerabilities": 10,
    "min_security_score": 80
  }
}
```

## Performance Features

- **Parallel Scanning**: Multiple security tools run concurrently
- **Caching**: Results cached to avoid repeated API calls
- **Incremental Analysis**: Only scan changed dependencies
- **Batch Processing**: Efficient handling of large dependency trees

## Best Practices

1. **Regular scanning** as part of development workflow
2. **Monitor security feeds** for new vulnerability disclosures
3. **Maintain updated dependencies** within risk tolerance
4. **Document license decisions** for compliance audit trail
5. **Automate security scanning** in CI/CD pipelines
6. **Review dependency additions** before merging

Works seamlessly with other Code Intelligence MCPs for comprehensive development security and compliance management.