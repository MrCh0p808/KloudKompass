# StatWoX Strategic Architecture (Phases 1-14)

This diagram outlines the complete multi-cloud technical ecosystem of StatWoX, organized by functional "Planes" as per the 2026 Enterprise Standards.

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#121214',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#00d4ff',
    'lineColor': '#00d4ff',
    'secondaryColor': '#1a1a1e',
    'tertiaryColor': '#09090b',
    'clusterBkg': 'rgba(0, 212, 255, 0.05)',
    'clusterBorder': 'rgba(0, 212, 255, 0.5)'
  }
}}%%

flowchart TB
    %% 3-Color Strict Palette: 
    %% 1. Background (Dark Gray/Black) 
    %% 2. Accent (Cyan #00d4ff)
    %% 3. Text (White #ffffff)

    classDef core fill:#121214,stroke:#00d4ff,stroke-width:2px,color:#ffffff
    classDef secondary fill:#1a1a1e,stroke:#ffffff,stroke-width:1px,color:#ffffff
    classDef cluster fill:transparent,stroke:#00d4ff,stroke-width:2px,stroke-dasharray: 5 5,color:#ffffff

    subgraph Management ["🛠️ ORCHESTRATION & DELIVERY"]
        GA["GitHub Actions (CI/CD)"]
        TF["Terraform (IaC)"]
        VAULT["Secrets Vault"]
    end

    subgraph Client ["🌐 USER ACCESS LAYER"]
        BROWSER["Browser / PWA (Next.js + React 19)"]
        subgraph Edge ["Edge Acceleration"]
            R53["Route53 (DNS)"]
            ACM["ACM (SSL/TLS)"]
            CF["CloudFront / Vercel (CDN & WAF)"]
        end
    end

    subgraph Security ["🛡️ SECURITY PERIMETER"]
        G["Edge Middleware (JWT / CSRF)"]
        H["Upstash Redis (Rate Limit / Bloom)"]
        IAM["AWS IAM (Access Control)"]
    end

    subgraph Compute ["⚙️ APPLICATION RUNTIME"]
        subgraph App ["Next.js Cluster"]
            NEXT["Next.js App Router"]
            LAMBDA["AWS Lambda (API Workers)"]
        end
        subgraph Logic ["Internal Engines"]
            AUTH["Auth & RBAC"]
            AI["GLM-5 AI Co-Pilot"]
            SYNC["Pusher Real-time"]
        end
    end

    subgraph Persistence ["🗄️ PERSISTENCE & STORAGE"]
        subgraph DB ["High-Frequency Data"]
            RDS[("AWS RDS Postgres")]
            NEON[("Neon Serverless Postgres")]
        end
        subgraph Storage ["Media & Assets"]
            S3[("AWS S3 / R2")]
        end
        QSTASH["Upstash QStash (Queues)"]
    end

    subgraph Observability ["👁️ OBSERVABILITY & HEALTH"]
        CW["CloudWatch (Logs/Metrics)"]
        SENTRY["Sentry (App Errors)"]
        AUDIT["Audit Logs (SQL Tracking)"]
        FUNNEL["PageView Funnels (UX Metrics)"]
    end

    %% Lifecycle Flows (Solid = Core Data, Dotted = Observability/Mgmt)
    TF -. "Provision" .-> CF & LAMBDA & RDS & S3
    GA -. "Deploy" .-> NEXT & LAMBDA
    VAULT -. "Inject Secrets" .-> NEXT & LAMBDA

    BROWSER --> R53
    R53 --> CF
    CF --> G
    G <--> H
    G ==> NEXT
    NEXT <--> LAMBDA
    
    LAMBDA --> Logic
    Logic <--> DB
    LAMBDA --> S3
    LAMBDA --> QSTASH

    %% Observability Streams
    LAMBDA -.-> CW
    RDS -.-> CW
    NEXT -.-> SENTRY
    DB -.-> AUDIT & FUNNEL
    CW -. "Alerts" .-> GA

    %% Apply 3-Color Theme
    class Management,Client,Security,Compute,Persistence,Observability cluster
    class GA,TF,VAULT,R53,ACM,CF,G,H,IAM,AUTH,AI,SYNC,CW,SENTRY,AUDIT,FUNNEL secondary
    class BROWSER,NEXT,LAMBDA,RDS,NEON,S3,QSTASH core
```

## Architectural Design Principles (Phase 10+ Standard)

### 1. Hybrid Provisioning Strategy
- **Infrastructure as Code (Terraform)**: All AWS resources (RDS, S3, CloudFront, VPC) are provisioned via Terraform to ensure environment parity and drift detection.
- **CI/CD (GitHub Actions)**: Every commit triggers a multi-stage pipeline that runs `vitest`, `biome` linting, and then deploys to BOTH Vercel (Front) and AWS Lambda (dedicated backend workers).

### 2. Multi-Layer Security Perimeter
- **CloudFront WAF**: Blocks SQL injection and bot traffic at the edge.
- **Next.js Middleware**: Edge-computed authentication checks using the `jose` library to prevent unauthenticated requests from hitting the database.
- **Upstash Redis Bloom Filters**: High-speed uniqueness checks for IP-based rate limiting (Phase 12 addition).

### 3. Distributed Observability Matrix
- **Infra Monitoring (CloudWatch)**: Monitors RDS connection pooling, Lambda execution duration, and Billing thresholds (`EstimatedCharges`).
- **App Monitoring (Sentry)**: Captures detailed stack traces and React hydration errors.
- **Activity Monitoring (Audit Logs)**: A database-native layer for tracing critical user-level changes (e.g., survey deletion).

### 4. Storage Decoupling
- **Neon/RDS Postgres**: Relational isolation for user profiles and survey metadata.
- **AWS S3 / Cloudflare R2**: Decoupled object storage for question images and file-uploads with zero-egress cost optimization.
- **Upstash QStash**: Asynchronous decoupling of long-running tasks (e.g., mass AI processing) from the main request/response cycle.
