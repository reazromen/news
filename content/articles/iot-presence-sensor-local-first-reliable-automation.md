---
title: "একটি ছোট IoT ডিভাইস কেন পুরো সার্ভারের ওপর নির্ভরশীল হওয়া উচিত নয়"
slug: "iot-presence-sensor-local-first-reliable-automation"
date: "2026-10-17T17:29:53+06:00"
updated: "2026-10-17T17:29:53+06:00"
source_name: "ESPHome"
source_url: "https://esphome.io/"
secondary_source_name: "Home Assistant"
secondary_source_url: "https://www.home-assistant.io/"
summary: "আমার desk-presence project-এ desktop IP ও server availability থেকে শেখা বিষয়: telemetry, decision-making এবং PC control-কে আলাদা করে ডিজাইন করা দরকার।"
category: "প্রযুক্তি"
status: "published"
wordpress_post_id: "777"
---

IoT project বানানোর সময় প্রথমে সবকিছু একসঙ্গে কাজ করানোই সবচেয়ে সহজ মনে হয়: sensor data একটি computer-এ পাঠানো, সেই computer-এ dashboard চালানো, আর সেখান থেকেই automation নিয়ন্ত্রণ করা। কিন্তু একটি dependency বন্ধ হলেই পুরো system অকার্যকর হয়ে যেতে পারে। আমার desk-presence project-এ এই বিষয়টি বাস্তবে চোখে পড়েছে।

সমস্যাটি কোথায় ছিল

আমার ESP8266 presence telemetry ও dashboard-এর একটি অংশ desktop-এর IP address এবং availability-এর ওপর নির্ভর করছিল। desktop বন্ধ বা network থেকে বিচ্ছিন্ন হলে dashboard-ও কাজ না করার পরিস্থিতি তৈরি হচ্ছিল। অথচ যে system-এর কাজ হলো desktop কখন ঘুমাবে বা জাগবে তা নিয়ন্ত্রণ করা, তার control path-ই desktop চালু থাকার ওপর নির্ভরশীল হলে architecture-এ একটি circular dependency তৈরি হয়।

তাই dashboard, listener এবং automation-কে always-on home server-এ সরানোর পথে এগিয়েছি। desktop এখন নিয়ন্ত্রণের লক্ষ্য—system-এর অপরিহার্য কেন্দ্র নয়। Wake-on-LAN-এর মাধ্যমে সেটিকে জাগানো যায়, আর ESP8266-এর local sensor logic-কে এমনভাবে রাখা দরকার যাতে server সাময়িকভাবে unavailable হলেও অন্তত sensor-এর মৌলিক আচরণ পুরোপুরি বন্ধ না হয়।

তিনটি দায়িত্ব আলাদা রাখা

**Sensor layer:** উপস্থিতি বা অনুপস্থিতির signal সংগ্রহ করবে, noise ও false trigger সামলাবে এবং নিজের health status জানাবে।

**Automation layer:** absence কতক্ষণ স্থায়ী হয়েছে, suspend delay কী, automation enabled কি না—এসব নিয়ম প্রয়োগ করবে।

**Control layer:** PC suspend বা Wake-on-LAN-এর মতো action চালাবে এবং action সফল হয়েছে কি না তা যাচাই করার সুযোগ দেবে।

এই স্তরগুলো আলাদা করলে একটি dashboard refresh ব্যর্থ হওয়া, server restart হওয়া, sensor Wi-Fi হারানো এবং PC suspend হওয়া—সবকিছুকে একই “system down” অবস্থার মধ্যে ফেলে দিতে হয় না। প্রতিটি অংশের health আলাদা করে দেখা যায়।

Local-first বনাম server-dependent design

এখানে “সবকিছু ESP8266-এই চালাতে হবে” এমন কোনো নিয়ম নেই। ছোট microcontroller-এর memory, processing ও connectivity সীমিত। ইতিহাস, remote access, authentication, dashboard এবং integration-এর জন্য server খুবই কার্যকর। কিন্তু server-কে প্রয়োজনীয়তার চেয়ে বেশি critical করে তোলা উচিত নয়। Sensor-এ local fallback রাখা এবং central server-এ richer automation চালানো—দুইয়ের সমন্বয় বেশি বাস্তবসম্মত হতে পারে।

এই চিন্তার সঙ্গে ESPHome ও Home Assistant-এর ecosystem-এ দেখা অনেক project-এর মিল আছে। ESPHome Presence Engine-এর মতো প্রকল্পে on-device analysis, state transitions এবং debouncing-এর ওপর জোর দেওয়া হয়েছে।

আমার design principle

Remote access দরকার, কিন্তু internet বা dashboard ছাড়া মৌলিক sensing যেন অকারণে থেমে না যায়। Central server দরকার, কিন্তু PC নিজে বন্ধ থাকলেও PC-কে জাগানোর পথ যেন থাকে। আর automation বন্ধ করলে live telemetry বন্ধ না হয়ে শুধু action নেওয়া বন্ধ হওয়া উচিত—কারণ monitoring ও control এক জিনিস নয়।

আমি এই system-কে শুধু একটি sensor gadget হিসেবে নয়, ছোট distributed system হিসেবে দেখি। এর reliability নির্ভর করবে শুধু hardware-এর ওপর নয়, dependency কোথায় রাখা হয়েছে এবং failure হলে কোন অংশ কীভাবে আচরণ করে—তার ওপরও।
