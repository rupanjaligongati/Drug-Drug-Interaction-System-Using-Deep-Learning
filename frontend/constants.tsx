
import React from 'react';

export const MOCK_HISTORY = [
  {
    id: 'h1',
    drugs: ['Aspirin', 'Warfarin'],
    riskLevel: 'HIGH',
    severity: 'SEVERE',
    confidenceScore: 0.94,
    timestamp: Date.now() - 1000000
  },
  {
    id: 'h2',
    drugs: ['Lisinopril', 'Amlodipine'],
    riskLevel: 'LOW',
    severity: 'MILD',
    confidenceScore: 0.88,
    timestamp: Date.now() - 5000000
  },
  {
    id: 'h3',
    drugs: ['Metformin', 'Glipizide'],
    riskLevel: 'MODERATE',
    severity: 'MODERATE',
    confidenceScore: 0.91,
    timestamp: Date.now() - 9000000
  }
];

export const DRUG_SUGGESTIONS = [
  'Aspirin', 'Warfarin', 'Lisinopril', 'Metformin', 'Simvastatin', 
  'Atorvastatin', 'Levothyroxine', 'Amlodipine', 'Metoprolol', 
  'Albuterol', 'Omeprazole', 'Losartan', 'Gabapentin', 'Hydrochlorothiazide',
  'Sertraline', 'Furosemide', 'Amoxicillin', 'Pantoprazole', 'Fluoxetine',
  'Metronidazole', 'Ciprofloxacin', 'Ibuprofen', 'Prednisone', 'Azithromycin'
];
