# WordPress publishing status

Last verified: 2026-10-16

## Current result

**A single test article is published in WordPress and publicly accessible. The automated publishing pipeline is not yet complete.**

### Verified test post

- Title: ঢাকা–কুমিল্লা ৮১ কিমি রেল কর্ড লাইনের প্রস্তাব, ব্যয় ৮৩,৯০১ কোটি টাকা
- WordPress post ID: 680
- Slug: `dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal`
- Public permalink: https://news.reazromen.com/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/
- WordPress REST API: `/wp-json/wp/v2/posts/680` reported `status=publish`, the expected link, and category metadata.
- WordPress RSS: https://news.reazromen.com/feed/ includes the post.
- Bangladesh category archive returned HTTP 200 and included the post.
- Article HTML includes the original conceptual SVG illustration and source links; the image URL returned HTTP 200.
- The image is embedded in the article body. WordPress `featured_media` is 0, so it is not configured as a featured image.

This was a one-off manual publication using a temporary PHP script and the WordPress bootstrap. It is not a reusable publisher integration, and the temporary script is not the production automation.

## Routing and site architecture

Caddy was validated and reloaded after a routing update. For `news.reazromen.com`:

- Existing static files/directories are served from the Git-built static site first.
- WordPress administrative, REST API, content, and related WordPress paths are proxied to the WordPress service.
- Paths without a matching static file/directory fall back to WordPress, enabling article permalinks.
- The root homepage remains the Git-built static homepage; it has not been replaced with the WordPress homepage.

Verified public routes returned HTTP 200 at the time of testing:

- `/`
- `/feed.xml`
- `/sitemap.xml`
- `/article/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/`
- `/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/`
- `/media/2e0f589cdd559def-dhaka-cumilla-rail-cord-illustration.svg`

Caddy configuration: `/home/romen/services/hserver-caddy/Caddyfile`

Pre-change backup: `/home/romen/services/hserver-caddy/Caddyfile.pre-wp-permalink-fallback-20261016`

## Canonical ownership

- Git Markdown remains the canonical source for the static news corpus.
- WordPress currently holds a separately published copy of the test article.
- Do not assume WordPress edits automatically sync back to Git.
- Define and implement an explicit conflict-aware sync policy before allowing edits in both systems to be authoritative.

## Not yet implemented / not yet verified

- No production-grade reusable WordPress publisher is connected to the Mesh AI/n8n workflow.
- No verified end-to-end run currently proves source collection → Mesh AI article generation → editorial/source validation → Git commit/deploy → WordPress publication.
- No retry, idempotency, or duplicate-recovery acceptance test exists for an automated WordPress publisher.
- WordPress featured-image metadata is not set for the test post.
- Do not claim scheduled news publishing is operational.

## Activation gates

1. Document the WordPress authentication method and store credentials only in an approved secret store; never in Git or workflow exports.
2. Implement a narrow publisher that accepts only validated articles and maps title, slug, body, excerpt, categories, source attribution, and approved media.
3. Add idempotency by stable slug/source identity; retries must not create duplicates.
4. Test in draft mode first; verify REST API output, public permalink, RSS/category visibility, image delivery, and error handling.
5. Run one explicitly approved single-post publish test through the actual automation path and retain its execution evidence.
6. Keep global/scheduled dispatch disabled until the complete test passes and an owner explicitly authorizes activation.

## Automation safety

The Content Studio publisher dispatch is expected to remain `PUBLISHER_DISPATCH_ENABLED=false`. The Facebook Content Agent n8n workflow remains inactive. Neither control is evidence that the separate news-to-WordPress pipeline is ready; they are safety controls for their respective systems.
