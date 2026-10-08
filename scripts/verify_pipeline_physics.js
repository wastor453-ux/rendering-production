/**
 * PRODUCTION PRE-RENDER VALIDATION SUITE
 */
const fs = require('fs');
const path = require('path');

function executeValidationPhysics(manifestPath) {
    console.log(`[VERIFY-PHYSICS] Auditing universal parameters inside: ${manifestPath}`);
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    const FPS = manifest.fps || 30;
    let fatalError = false;
    let errorDump = [];

    // 1. DYNAMIC DATA MONOTONICITY TRACKER
    if (manifest.dataSeries) {
        manifest.dataSeries.forEach((series, index) => {
            const data = series.values;
            const step = series.step || 1;

            if (series.property === 'cumulative_trend' || series.property === 'growth_metric') {
                for (let n = 1; n < data.length; n++) {
                    const velocity = (data[n] - data[n - 1]) / step;
                    if (velocity < 0) {
                        fatalError = true;
                        errorDump.push({
                            module: 'MONOTONICITY',
                            message: `Invalid velocity drop. Series ${index} dips at n=${n}. V[n]=${velocity}`
                        });
                    }
                }
            }

            // A loss/decay trend is honest only while it never rises.
            // Any positive jump (e.g. a data typo flipping a loss into a
            // phantom gain) is a FATAL fabrication of the displayed metric.
            if (series.property === 'decay_metric') {
                for (let n = 1; n < data.length; n++) {
                    const velocity = (data[n] - data[n - 1]) / step;
                    if (velocity > 0) {
                        fatalError = true;
                        errorDump.push({
                            module: 'MONOTONICITY_DECAY',
                            message: `Invalid velocity rise. Decay series ${index} rises at n=${n}. V[n]=${velocity}`
                        });
                    }
                }
            }
        });
    }

    // 2. 2D VIEWPORT BOX AXIS-ALIGNED COLLISION MATRIX (AABB)
    const SAFE_MARGIN = 80;
    if (manifest.layoutFrames) {
        manifest.layoutFrames.forEach((frameObj, frameIndex) => {
            const elements = frameObj.elements;
            
            // Check bounding boxes for overlaps and screen border safe area cuts
            for (let i = 0; i < elements.length; i++) {
                const el = elements[i];
                if (el.x1 < SAFE_MARGIN || el.x2 > (1920 - SAFE_MARGIN) || el.y1 < SAFE_MARGIN || el.y2 > (1080 - SAFE_MARGIN)) {
                    fatalError = true;
                    errorDump.push({
                        module: 'SAFE_ZONE_VIOLATION',
                        message: `Element '${el.id}' breaches the 80px platform UI buffer zone at frame ${frameIndex}.`
                    });
                }
                
                for (let j = i + 1; j < elements.length; j++) {
                    const target = elements[j];
                    const collisionX = el.x1 < target.x2 && el.x2 > target.x1;
                    const collisionY = el.y1 < target.y2 && el.y2 > target.y1;
                    
                    if (collisionX && collisionY) {
                        fatalError = true;
                        errorDump.push({
                            module: 'AABB_COLLISION',
                            message: `Layout clash! Element '${el.id}' intersects with '${target.id}' at frame ${frameIndex}.`
                        });
                    }
                }
            }
        });
    }

    if (fatalError) {
        console.error("[FATAL] PHYSICS VALIDATION SUITE REJECTED BUILD.");
        console.error(JSON.stringify(errorDump, null, 2));
        fs.writeFileSync('verify-report-physics.json', JSON.stringify(errorDump, null, 2));
        process.exit(1);
    } else {
        console.log("[VERIFY-PHYSICS] ALL REFINED TREND MATRIX TESTS LOGGED: 100% PASS.");
        process.exit(0);
    }
}

const args = process.argv.slice(2);
if (args[0]) executeValidationPhysics(args[0]);
