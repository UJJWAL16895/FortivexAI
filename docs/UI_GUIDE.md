# Showcase guide

Open / for the overview and /console for the working console. The route entry in frontend/src/main.jsx loads either page separately. Showcase.jsx contains the hero, section list, worked example, architecture controls and scenario values. Console.jsx contains the actual mic button, provider trace, CRM and Insights.

- Change the hero text in Showcase.jsx inside the section with id home.
- Add or edit a feature in the features list at the top of Showcase.jsx.
- Change the accent at --accent and --glow in showcase.css. Check contrast against the background.
- Change wave timing in the signal animation. IntersectionObserver highlights the flow and reveals cards. Reduced motion disables the waveform animation and parallax.
- The sample array contains the local script. Its claims and numbers are illustrative. Keep real observations synced with SCALABILITY.md and COSTS.md.

## Quiz

1. **Where is the real console?** At /console.
2. **Does the local script spend quota?** It plays locally from the array.
3. **Where does the wave in the console get its signal?** A Web Audio analyser reads the active mic stream.
4. **How does reduced motion work?** The CSS media query stops animation and JavaScript skips parallax and typing.
5. **Where do scenario costs come from?** COSTS.md, including its assumptions.
