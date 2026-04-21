---
title: Data Schemas for Plant Tracking System Frontend
---
# Data Schemas

The frontend processes plant data in TypeScript interfaces that mirror the markdown-based storage format. These schemas define the structure of plant records, seed packet information, care activities, and environmental data exchanged between frontend components and the backend API.

## Core Plant Record

The `PlantRecord` interface represents a complete plant tracking entry, combining immutable seed packet data with mutable growth observations and care activities.

```typescript
interface PlantRecord {
  plantId: string;          // VARIETY-YYYY-SEQ format
  seedPacket: SeedPacketInfo;
  plantingDates: PlantingDates;
  status: PlantStatus;
  environment: EnvironmentLog[];
  care: CareLog[];
  observations: ObservationLog[];
  photos: PhotoLog[];
}
```

### Seed Packet Information

Immutable data captured from seed packets at initial planting.

```typescript
interface SeedPacketInfo {
  varietyName: string;
  latinName: string;
  brand: string;
  daysToMaturity: number;   // days from transplant to harvest
  germinationTime: {        // range in days
    min: number;
    max: number;
  };
  plantingDepth: {          // in inches
    min: number;
    max: number;
  };
  spacing: {                // in inches
    min: number;
    max: number;
  };
  sunRequirements: SunExposure; // enum: full_sun, partial_sun, shade
  indoorStartTime: number;  // weeks before last frost to start indoors
}
```

### Planting Dates and Status

```typescript
interface PlantingDates {
  planned: string;          // ISO date string (YYYY-MM-DD)
  actual?: string;          // actual planting date if different
}

interface PlantStatus {
  indoor: boolean;
  location: string;         // e.g., "garden bed 3, row 2" or "indoor seed tray"
  lastUpdated: string;      // ISO timestamp
}
```

## Activity Logs

All temporal data follows a timestamped log pattern for auditability and chronological sorting.

```typescript
interface EnvironmentLog {
  timestamp: string;        // ISO timestamp
  temperature: {            // in Fahrenheit
    high: number;
    low: number;
  };
  humidity: number;         // percentage
  rainfall: number;         // inches since last reading
  sunlight: SunExposure;    // current conditions
  notes?: string;
}

interface CareLog {
  timestamp: string;        // ISO timestamp
  type: CareType;           // enum: watering, fertilizing, soil_amendment, pruning, staking, pest_treatment
  details: CareDetails;     // union type based on care type
}

interface ObservationLog {
  timestamp: string;        // ISO timestamp
  note: string;
  severity?: ObservationSeverity; // enum: info, warning, critical
}

interface PhotoLog {
  timestamp: string;        // ISO timestamp
  url: string;              // relative path or base64 encoded
  description?: string;
  latitude?: number;        // optional geotagging
  longitude?: number;
}
```

### Care Details Union

Specific details vary by care activity type.

```typescript
type CareDetails =
  | WateringDetails
  | FertilizingDetails
  | SoilAmendmentDetails
  | PruningDetails
  | StakingDetails
  | PestTreatmentDetails;

interface WateringDetails {
  amount: number;           // in gallons
  method: WateringMethod;   // enum: hand, drip, sprinkler
}

interface FertilizingDetails {
  fertilizer: string;       // name or N-P-K ratio
  amount: number;           // in ounces or grams
  strength: FertilizerStrength; // enum: quarter, half, full
}

interface SoilAmendmentDetails {
  amendment: string;        // e.g., "compost", "lime", "sulfur"
  amount: number;           // volume or weight
  unit: string;             // e.g., "cups", "pounds"
}

interface PruningDetails {
  type: PruneType;          // enum: deadheading, thinning, shaping
  amount: string;           // descriptive (e.g., "removed 3 yellow leaves")
}

interface StakingDetails {
  method: StakeMethod;      // enum: cage, trellis, single_stake
  material: string;         // e.g., "bamboo", "metal"
}

interface PestTreatmentDetails {
  pest: string;             // observed pest name
  treatment: string;        // e.g., "neem oil", "insecticidal soap"
  amount: number;           // application amount
  unit: string;             // e.g., "teaspoons", "ml"
}
```

## Enumerations

```typescript
type SunExposure = 'full_sun' | 'partial_sun' | 'shade';
type CareType = 
  | 'watering' 
  | 'fertilizing' 
  | 'soil_amendment' 
  | 'pruning' 
  | 'staking' 
  | 'pest_treatment';
type WateringMethod = 'hand' | 'drip' | 'sprinkler';
type FertilizerStrength = 'quarter' | 'half' | 'full';
type PruneType = 'deadheading' | 'thinning' | 'shaping';
type StakeMethod = 'cage' | 'trellis' | 'single_stake';
type ObservationSeverity = 'info' | 'warning' | 'critical';
```

## API Response Wrappers

Backend endpoints return standardized response envelopes.

```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

interface PaginatedApiResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}
```

## PRD Traceability

- FR6: Plant records with core attributes - `PlantRecord` and `SeedPacketInfo`
- FR7: Markdown file storage - schemas map to markdown frontmatter and sections
- FR8: Timestamped notes - `ObservationLog` and all log entries
- FR9: Photo attachment - `PhotoLog`
- FR10: Record updates over time - temporal arrays in `PlantRecord`
- FR11: Searchable database - frontend uses these schemas for filtering/sorting
- FR22-FR30: Environmental and care tracking - `EnvironmentLog` and `CareLog` with union types
- FR31-FR35: Multi-source data - schemas accommodate manual and automated data
- FR36-FR40: Hermes agent integration - schemas define data structures for natural language querying
- FR41-FR45: Mobile interface - schemas drive form validation and display logic in frontend components

## Storage Mapping Note

While the backend stores data in markdown files, the frontend consumes and produces data conforming to these TypeScript interfaces. The backend API translates between markdown format and JSON representations using these schemas as the contract.

Example markdown-to-JSON mapping:
- Markdown frontmatter → `PlantRecord` top-level fields
- Markdown sections → `environment`, `care`, `observations`, `photos` arrays
- Each log entry corresponds to a markdown subsection with timestamp heading