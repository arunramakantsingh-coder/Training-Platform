export type IihtModule = {
  number: number;
  title: string;
  hours: number;
  summary: string;
  topics: string[];
};

export type IihtDay = {
  day: number;
  focus: string;
  theory: number;
  lab: number;
  topics: string;
  handsOn: string;
};

export const iihtCourse = {
  title: "Arista VeloCloud SD-WAN",
  subtitle: "40-Hour Instructor-Led Training & Hands-On Lab",
  audience: "IIHT / Techademy Cohort",
  participants: 25,
  duration: "40 hours",
  delivery: "Online",
  schedule: "10 days · 4 hours/day",
  theoryHours: 17,
  labHours: 23,
  level: "Professional / Lateral",
  modules: [
    { number: 1, title: "VeloCloud Architecture & Fundamentals", hours: 4, summary: "Architecture, terminology and the VeloCloud control, gateway and edge model.", topics: ["SD-WAN fundamentals", "Orchestrator, Gateway and Edge roles", "Underlay / overlay", "VeloCloud architecture"] },
    { number: 2, title: "Orchestrator Administration", hours: 4, summary: "Administration workflows, tenants, users, dashboards and operational navigation.", topics: ["Tenant administration", "User and access administration", "Dashboard navigation", "Orchestrator workflows"] },
    { number: 3, title: "Edge Deployment", hours: 4, summary: "Edge models, onboarding, ZTP, activation and initial connectivity.", topics: ["Edge models", "ZTP and activation", "WAN interfaces", "Edge-to-Orchestrator workflow"] },
    { number: 4, title: "Edge Configuration & High Availability", hours: 4, summary: "Branch configuration, profiles, device settings and HA scenarios.", topics: ["Profiles and configuration hierarchy", "Device settings", "LAN/WAN configuration", "High availability"] },
    { number: 5, title: "Routing & Traffic Engineering", hours: 4, summary: "Routing, route exchange, traffic engineering and dynamic path selection.", topics: ["Static routing", "BGP / OSPF considerations", "Route advertisement", "Dynamic path selection"] },
    { number: 6, title: "Business Policies & Application Steering", hours: 4, summary: "Application awareness, business policies, traffic steering and QoS.", topics: ["Business policies", "Application identification", "Traffic steering", "QoS and link steering"] },
    { number: 7, title: "WAN Optimization & Performance", hours: 4, summary: "Path optimization and performance techniques for impaired WAN conditions.", topics: ["Dynamic path selection", "Link remediation", "Packet duplication", "FEC, jitter, latency and loss"] },
    { number: 8, title: "Security & Segmentation", hours: 4, summary: "Segmentation, firewall policies, secure Internet access and multi-tenant design.", topics: ["Network segmentation", "Firewall policies", "Secure Direct Internet Access", "Multi-tenant design"] },
    { number: 9, title: "Monitoring & Operational Support", hours: 4, summary: "Operational visibility, health monitoring, analytics, events and capacity.", topics: ["Dashboard monitoring", "Link health", "Application performance", "Events, alerts and capacity planning"] },
    { number: 10, title: "Troubleshooting & Software Lifecycle", hours: 4, summary: "Troubleshooting methodology, diagnostics, upgrades, backup and restore.", topics: ["Edge and tunnel troubleshooting", "Routing and application issues", "Packet capture and diagnostics", "Upgrade, backup and restore"] },
    { number: 11, title: "Migration Knowledge Transfer & Capstone", hours: 4, summary: "Viptela-to-VeloCloud mapping, operational differences and end-to-end implementation.", topics: ["Cisco Viptela mapping", "Operational process differences", "Monitoring and troubleshooting differences", "End-to-end capstone"] }
  ] satisfies IihtModule[],
  days: [
    { day: 1, focus: "VeloCloud Architecture & Fundamentals", theory: 2, lab: 2, topics: "Architecture, terminology, components, underlay/overlay and SD-WAN concepts.", handsOn: "Lab orientation, environment access, component identification and basic connectivity." },
    { day: 2, focus: "Orchestrator, Gateway & Edge Deployment", theory: 2, lab: 2, topics: "Orchestrator workflow, Gateway functions, Edge models, onboarding and templates.", handsOn: "Edge onboarding, initial configuration, WAN links and connectivity validation." },
    { day: 3, focus: "Profiles, Segments & Configuration", theory: 2, lab: 2, topics: "Configuration hierarchy, profiles, device settings, segments and inheritance.", handsOn: "Create/modify profiles, configure segments and validate configuration inheritance." },
    { day: 4, focus: "Routing & Dynamic Path Selection", theory: 2, lab: 2, topics: "Routing, BGP/OSPF considerations, route exchange, path selection and traffic engineering.", handsOn: "Configure routing scenarios, test path selection and observe path changes." },
    { day: 5, focus: "Business Policies, Application Awareness & QoS", theory: 2, lab: 2, topics: "Business policies, application identification, steering, QoS and performance.", handsOn: "Create policies, test traffic steering and validate preferred/failover paths." },
    { day: 6, focus: "VPN, Segmentation & Hybrid WAN", theory: 2, lab: 2, topics: "Segmentation, VPN concepts, branch connectivity, hub-and-spoke and hybrid WAN.", handsOn: "Build segmented networks, configure VPN connectivity and validate isolation." },
    { day: 7, focus: "Internet, MPLS & Cloud Connectivity", theory: 2, lab: 2, topics: "Internet/MPLS underlay options, cloud connectivity and service insertion.", handsOn: "Build a representative hybrid WAN and validate Internet/MPLS paths." },
    { day: 8, focus: "Monitoring, Analytics & Operations", theory: 1.5, lab: 2.5, topics: "Operational visibility, events, application/link analytics and performance interpretation.", handsOn: "Use dashboards and diagnostics, analyze link/application behavior and perform health checks." },
    { day: 9, focus: "Troubleshooting, Resilience & Recovery", theory: 1.5, lab: 2.5, topics: "Troubleshooting methodology, failures, resilience and recovery.", handsOn: "Fault injection, Edge/link failure scenarios, troubleshooting and service restoration." },
    { day: 10, focus: "End-to-End Capstone Implementation", theory: 1, lab: 3, topics: "Architecture review, design decisions and assessment criteria.", handsOn: "End-to-end implementation, routing, policies, failover, validation and final assessment." }
  ] satisfies IihtDay[]
};

export const labPortalFeatures = [
  { title: "Dedicated student environment", detail: "One logically isolated lab environment per participant." },
  { title: "Guided hands-on exercises", detail: "Lab activities follow the 40-hour curriculum and daily delivery plan." },
  { title: "Reset / re-provision", detail: "The portal is designed for rapid recovery between exercises." },
  { title: "Lab access status", detail: "A future Lab Controller connection will expose real-time environment state." }
];
