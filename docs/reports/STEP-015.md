# STEP-015 · Showcase

Before, the root opened straight into the operator console. Now the root explains the project and plays a scripted sample. The existing console is at /console. The sample uses an in-bundle fixture and can run with external requests blocked.

[VERIFIED] Chrome showed no horizontal overflow at 390, 768 and 1440 px. The test checks the skip link, nav targets, playback of the sample and keyboard focus, architecture selection and console connection. The mock Chrome microphone check used a synthetic capture device and successfully played and confirmed its reply. The text hero also verified the CRM and Insights panels. Desktop and mobile captures are in diagrams/ui.

[VERIFIED] Vite output was 222.05 kB for the shared JS entry, 11.22 kB for the route-lazy showcase and 15.81 kB for the route-lazy console. Gzip output was 69.68, 4.16 and 5.48 kB respectively. Lighthouse 13.6.0 on Windows Chrome against localhost returned Performance 98, Accessibility 100 and color contrast pass. That is one mobile-profile lab run. User hardware performance remains unmeasured. [Guide and quiz](../UI_GUIDE.md)
