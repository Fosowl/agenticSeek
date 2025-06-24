import { useEffect, useRef } from 'react';
/**
 * Custom hook that sets up an interval to call a callback function at specified intervals.
 * @param {function} callback - The function to be called at each interval.
 * @param {number} delay - The interval time in milliseconds. If null, the interval is cleared.
 */

export function useInterval(callback, delay) {
    const savedCallback = useRef();
    // Remember the latest callback.
    useEffect(() => {
        savedCallback.current = callback;
    }, [callback]);

    // Set up the interval.
    useEffect(() => {
        function tick() {
            savedCallback.current();
        }
        if (delay !== null) {
            let id = setInterval(tick, delay);
            return () => clearInterval(id);
        }
    }, [delay]);
}