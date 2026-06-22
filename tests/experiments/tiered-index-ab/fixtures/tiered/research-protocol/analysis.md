# Analysis and Reporting Standards

## Statistical Requirements
- Report sample size for all analyses
- Confidence intervals required (95% CI default)
- Effect size measures required (Cohen's d, odds ratio, etc.)
- p-values reported to 4 decimal places (never "p < 0.05" alone)

## Data Cleaning
- Document all cleaning steps in the analysis notebook
- Missing data handling: report percentage missing, justify imputation method
- Outlier detection: IQR method with 1.5x threshold
- Duplicate detection: exact match on key fields + fuzzy match on text fields (>95% similarity)

## Reproducibility
- Random seeds set and recorded for all stochastic processes
- Environment captured: Python version, package versions, OS
- Data snapshots versioned (date-stamped copies in cold storage)
- Analysis scripts must run end-to-end from raw data to final output

## Bias Awareness
- Selection bias: document how data sources were chosen
- Survivorship bias: document what data is NOT in the dataset
- Temporal bias: document the time period and any seasonal effects
- Measurement bias: document instrument precision and known limitations

## Report Structure
Every research report must include:
1. **Executive summary** (1 paragraph, key findings)
2. **Methodology** (data sources, collection method, analysis approach)
3. **Results** (findings with statistical support)
4. **Limitations** (what this analysis cannot tell you)
5. **Recommendations** (actionable next steps)
6. **Appendix** (raw data references, code links, supplementary tables)

## Visualization Standards
- All charts must have: title, axis labels, units, legend
- Color scheme: use colorblind-safe palettes (viridis, cividis)
- Bar charts for categorical comparisons, line charts for trends
- No 3D charts, no pie charts for >5 categories
- Interactive dashboards use Plotly or Observable

## Peer Review
- All research reports require peer review before publication
- Reviewer must reproduce at least one key finding
- Review checklist: methodology sound, conclusions supported, limitations stated
- Turn-around time: 5 business days for standard review, 2 days for urgent

## Data Privacy and Ethics

### PII Handling
- No PII in research datasets — pseudonymize before analysis
- Pseudonymization mapping stored separately with restricted access
- Re-identification risk assessment required for any published dataset
- Data retention: raw research data retained for 2 years, then purged

### Consent and Compliance
- User consent required for any behavioral data collection
- GDPR-compliant data processing agreements with all data providers
- Data Processing Impact Assessment (DPIA) required for new data sources
- Right to erasure: ability to purge individual records within 30 days

### Ethical Guidelines
- No deceptive research practices
- Results reported honestly — negative findings are still findings
- Conflicts of interest disclosed in all publications
- Open methodology preferred — proprietary methods documented internally

## Tool Standards

### Notebooks
- Jupyter notebooks for exploratory analysis
- Convert to Python scripts for production pipelines
- Notebooks must run top-to-bottom without manual intervention
- Clear all outputs before committing (use `nbstripout`)

### Version Control for Research
- Data version control (DVC) for large datasets
- Git for code and analysis scripts
- Branch per experiment: `research/{experiment-name}`
- Tag releases: `data-v{date}` for dataset snapshots

### Compute Resources
- Local development: CPU only, datasets < 1GB
- Cloud compute: GPU for ML tasks, requested via the research team Slack channel
- Cost tracking: tag all cloud resources with project ID
- Auto-shutdown: development instances turn off after 2 hours of inactivity

## Quality Gates — Before Starting Analysis
- [ ] Data collection complete and validated
- [ ] Missing data <5% (or justification for proceeding with more)
- [ ] Cleaning steps documented
- [ ] Analysis plan written (pre-registration recommended)

## Quality Gates — Before Publishing Results
- [ ] Peer review completed
- [ ] Key finding reproduced by reviewer
- [ ] Limitations section complete
- [ ] All visualizations meet standards
- [ ] Data archived with version tag
