# Mock Cost Savings Scenario

## Simulated Production Environment

This demonstrates the scanner's impact in a typical development team environment.

### Scenario: 10-Person Dev Team, 3 Months of Accumulation

**Idle EC2 Instances:**
- 5x t2.medium instances (forgotten test environments) @ $33.41/month each = $167.05/month
- 3x t2.small instances (old staging servers) @ $16.79/month each = $50.37/month
- 2x t3.small instances (abandoned POCs) @ $15.19/month each = $30.38/month

**Unattached EBS Volumes:**
- 8x 50GB volumes (from terminated instances) @ $5.00/month each = $40.00/month
- 5x 100GB volumes (old snapshots' base volumes) @ $10.00/month each = $50.00/month
- 12x 20GB volumes (forgotten test data) @ $2.00/month each = $24.00/month

**Total Monthly Waste: $361.80**

**Annual Impact: $4,341.60**

### Detection Results

**Scanner Findings:**
```
Idle EC2 Instances: 10
- Average CPU utilization: 1.2% over 7 days
- Total compute waste: $247.80/month

Unattached EBS Volumes: 25
- Total capacity: 1,540 GB
- Total storage waste: $114.00/month

Total Potential Savings: $361.80/month
```

### Actions Taken

After receiving the daily email report:
1. Stopped all 10 idle instances → Saved $247.80/month
2. Created snapshots of 8 volumes with valuable data → Deleted volumes
3. Deleted 17 volumes with no valuable data → Saved $114.00/month

**Result: $361.80/month savings = $4,341.60/year**

### ROI Analysis

- **Time to build scanner:** 3 days
- **Time to review daily reports:** 5 minutes/day
- **Monthly time investment:** ~2.5 hours
- **Cost savings per hour of maintenance:** $144.72/hour

### Extrapolation to Enterprise Scale

A company with 50 developers across 5 teams:
- Estimated waste: $361.80 × 5 teams = **$1,809/month**
- Annual savings: **$21,708**
- 10-year savings: **$217,080**

---

## My Test Environment Results

In my free-tier test setup:
- 1x t2.micro instance (0.3% CPU) = $7.49/month
- 1x 8GB unattached volume = $0.80/month
- **Total: $8.29/month**

While modest, this demonstrates the scanner's ability to detect waste. Scaled to a production environment with multiple teams, the impact is substantial.