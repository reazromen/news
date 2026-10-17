---
title: "কম্পিউটার ব্যবহার না করলে নিজে থেকেই ঘুমাবে: আমার ESP8266 Power-Saving Experiment"
slug: "esp8266-presence-aware-pc-power-saving"
date: "2026-10-17T17:29:53+06:00"
updated: "2026-10-17T17:29:53+06:00"
source_name: "ESPHome community-র mmWave ও PIR project"
source_url: "https://community.home-assistant.io/t/low-latency-presence-sensor-mmwave-pir-using-esphome/407553"
summary: "ESP8266 দিয়ে ডেস্কে উপস্থিতি শনাক্ত করে PC suspend এবং Wake-on-LAN নিয়ন্ত্রণের পরীক্ষা থেকে আমার পর্যবেক্ষণ: power saving শুধু hardware নয়, automation design-এরও বিষয়।"
category: "প্রযুক্তি"
status: "published"
wordpress_post_id: "776"
---

কম্পিউটার চালু রেখে অন্য কাজে চলে যাওয়া খুব সাধারণ অভ্যাস। কয়েক মিনিটের জন্য উঠে গেলে অনেক সময় PC ঘণ্টার পর ঘণ্টা idle অবস্থায় চলে। আমার প্রশ্ন ছিল সহজ: ডেস্কে কেউ আছে কি না, একটি ছোট IoT ডিভাইস সেটি বুঝতে পারলে কম্পিউটারকে কখন ঘুমাতে হবে তা কি স্বয়ংক্রিয়ভাবে ঠিক করা যায়?

এই ভাবনা থেকেই ESP8266-ভিত্তিক desk-presence system নিয়ে কাজ করছি। লক্ষ্য শুধু sensor-এর মান dashboard-এ দেখানো নয়; উপস্থিতি ও অনুপস্থিতির তথ্য ব্যবহার করে PC suspend করা, প্রয়োজন হলে Wake-on-LAN দিয়ে আবার জাগানো, এবং পুরো প্রক্রিয়াটি পর্যবেক্ষণযোগ্য রাখা।

আমার প্রধান পর্যবেক্ষণ: power saving মানে শুধু কম watt খরচের যন্ত্র কেনা নয়

Power saving নিয়ে আলোচনা হলে সাধারণত CPU, power supply, monitor বা বিদ্যুতের rate নিয়ে কথা হয়। কিন্তু software ও automation-এর সিদ্ধান্তও গুরুত্বপূর্ণ। কাজের জায়গা ফাঁকা থাকলে PC-কে suspend করা যেতে পারে; আবার কেউ ডেস্কে বসে থাকলে ভুল করে suspend হয়ে যাওয়াও চলবে না। তাই একটি sensor signal পেলেই সঙ্গে সঙ্গে power state বদলে দেওয়া যথেষ্ট নয়। debounce, absence timeout, configurable delay এবং status feedback দরকার।

আমার dashboard-এ Away-to-suspend delay বেছে নেওয়ার ধারণাটি এসেছে এই বাস্তব সমস্যা থেকেই। কারও জন্য এক মিনিট যথেষ্ট, আবার কারও কাজের ধরন অনুযায়ী পাঁচ বা দশ মিনিট, এমনকি আরও বেশি সময় প্রয়োজন হতে পারে। “Presence নেই” আর “এখনই suspend করতে হবে”—এই দুটি একই ঘটনা নয়।

কেন আমি এখনই নির্দিষ্ট বিদ্যুৎ সাশ্রয়ের দাবি করছি না

এটি একটি engineering experiment; calibrated power meter দিয়ে আগে ও পরে watt-hour মেপে তুলনা না করা পর্যন্ত নির্দিষ্ট শতাংশ সাশ্রয়ের দাবি করা ঠিক হবে না। ফলাফল নির্ভর করবে PC-এর hardware, idle power draw, monitor, suspend mode, প্রতিদিনের ব্যবহার এবং কতক্ষণ অনুপস্থিত থাকা হয় তার ওপর। আমার কাছে গুরুত্বপূর্ণ হলো এমন একটি system তৈরি করা, যার আচরণ বোঝা যায় এবং ভুল হলে কারণ খুঁজে পাওয়া যায়।

বিশ্বজুড়ে ব্যবহৃত ধারণার সঙ্গে এর যোগ

Home Assistant ও ESPHome-এর কমিউনিটিতে presence-aware lighting, room occupancy এবং sensor automation নিয়ে বহু DIY project আছে। যেমন ESPHome community-র mmWave ও PIR project দ্রুত detection এবং false trigger কমানোর সমস্যাগুলো নিয়ে আলোচনা করে। একই মূল ধারণা এখানে কাজে লাগে: sensor data-কে সরাসরি action বানানোর আগে নির্ভরযোগ্য state-এ রূপান্তর করা। তবে আমার ব্যবহারের ক্ষেত্রটি ঘরের আলো নয়—কম্পিউটারের power state।

পরবর্তী ধাপ

পরবর্তী ধাপে আমি real-world false trigger, suspend delay, wake-up reliability এবং দীর্ঘ সময়ের uptime পর্যবেক্ষণ করতে চাই। Dashboard-এ state দেখা, “Send Magic Packet” দিয়ে PC জাগানো এবং automation বন্ধ থাকলেও live sensor telemetry দেখা—এসব আলাদা করে যাচাই করা দরকার।

আমার কাছে এই প্রকল্পের মূল শিক্ষা হলো: ভালো power-saving automation ব্যবহারকারীর কাজকে বাধা না দিয়ে পেছনে কাজ করবে। আর সাশ্রয়ের দাবি হবে measurement-ভিত্তিক, অনুমানভিত্তিক নয়।
