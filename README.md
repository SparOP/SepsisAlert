# 🩺 SepsisAlert

### AI-Powered Early Sepsis Screening for Community Health Workers

SepsisAlert is an AI-powered sepsis screening system designed to assist ASHA workers and community health workers in identifying patients who may require further medical evaluation.

The system combines low-cost physiological sensors with a machine learning model deployed in the cloud. Heart rate, SpO₂, and temperature are collected using an ESP32-based device, transmitted to a web application over Bluetooth, and sent to a cloud-based ML inference pipeline. The system returns a sepsis risk score that is converted into a simple risk category for the healthcare worker.

> **SepsisAlert is a screening and decision-support tool, not a medical diagnostic system.**

---

## 🏆 Project Achievement

**Winner — IEM/UEM Department of Computer Applications Project Competition, February 2026**

---

## 🎯 Problem

Sepsis is a life-threatening condition where the body's response to infection can lead to organ dysfunction.

In rural and resource-constrained environments, community health workers may not have access to sophisticated diagnostic infrastructure.

SepsisAlert explores whether a small number of easily measurable physiological signals can be used to provide an early risk flag and support referral decisions.

---

## 💡 Solution

SepsisAlert connects three inexpensive physiological sensors to a machine learning pipeline:

- ❤️ **Heart Rate**
- 🫁 **SpO₂**
- 🌡️ **Body Temperature**

The readings are collected by an ESP32 and transmitted to a web application using Bluetooth Low Energy (BLE).

The application sends the data to an AWS-based inference pipeline, where a trained Random Forest classifier generates a sepsis risk score.

The result is presented to the healthcare worker using a simple risk classification:

| Risk Level | Model Score |
|------------|-------------|
| 🔴 High | ≥ 0.05 |
| 🟠 Medium | 0.03 – < 0.05 |
| 🟢 Low | < 0.03 |

The threshold was selected through threshold tuning with a focus on achieving higher recall for the screening use case.

---

# 🏗️ System Architecture

```text
┌──────────────────────┐
│       Patient        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│ ESP32 + Sensors              │
│                              │
│ • MAX30102 → HR + SpO₂      │
│ • DS18B20  → Temperature    │
└──────────┬───────────────────┘
           │
           │ Bluetooth Low Energy
           ▼
┌──────────────────────────────┐
│ Next.js Web Application      │
│                              │
│ Web Bluetooth API            │
└──────────┬───────────────────┘
           │
           │ HTTP POST
           ▼
┌──────────────────────────────┐
│ AWS API Gateway              │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ AWS Lambda                   │
│                              │
│ • Request handling           │
│ • Preprocessing              │
│ • ML inference coordination  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Amazon SageMaker             │
│                              │
│ Deployed Random Forest       │
│ 400 Decision Trees           │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Sepsis Risk Score            │
│                              │
│ High / Medium / Low          │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Next.js Web Application      │
│                              │
│ Result displayed to          │
│ community health worker      │
└──────────────────────────────┘
