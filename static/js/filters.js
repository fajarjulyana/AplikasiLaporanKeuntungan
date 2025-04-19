/**
 * Filters.js - Handles date filtering functionality
 * 
 * This script manages the date filter form, providing pre-set date ranges
 * and ensuring proper date validation.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get date filter form elements
    const filterForm = document.querySelector('form');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    // Add event listeners for date validation
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', validateDates);
        endDateInput.addEventListener('change', validateDates);
    }
    
    // Add preset date range buttons if filter form exists
    if (filterForm) {
        addPresetDateRanges();
    }
    
    /**
     * Validates that the end date is not before the start date
     */
    function validateDates() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        
        if (startDate && endDate && startDate > endDate) {
            alert('End date cannot be earlier than start date');
            endDateInput.value = startDate;
        }
    }
    
    /**
     * Adds preset date range buttons to the filter form
     */
    function addPresetDateRanges() {
        // Create a container for preset buttons
        const presetContainer = document.createElement('div');
        presetContainer.className = 'mt-3';
        presetContainer.innerHTML = '<label class="form-label">Quick Selections:</label>';
        
        // Create row for buttons
        const buttonRow = document.createElement('div');
        buttonRow.className = 'btn-group w-100';
        
        // Define preset ranges
        const presets = [
            { label: 'Today', days: 0 },
            { label: 'Last 7 Days', days: 7 },
            { label: 'Last 30 Days', days: 30 },
            { label: 'This Month', type: 'month' },
            { label: 'This Year', type: 'year' },
            { label: 'All Time', type: 'all' }
        ];
        
        // Create buttons for each preset
        presets.forEach(preset => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn btn-outline-secondary btn-sm';
            button.textContent = preset.label;
            button.addEventListener('click', () => setDateRange(preset));
            buttonRow.appendChild(button);
        });
        
        // Add the buttons to the container and the container to the form
        presetContainer.appendChild(buttonRow);
        filterForm.querySelector('.row').after(presetContainer);
    }
    
    /**
     * Sets date range based on the selected preset
     * @param {Object} preset - The preset configuration
     */
    function setDateRange(preset) {
        const today = new Date();
        let start = new Date(today);
        let end = new Date(today);
        
        if (preset.type === 'month') {
            // First day of current month
            start = new Date(today.getFullYear(), today.getMonth(), 1);
        } else if (preset.type === 'year') {
            // First day of current year
            start = new Date(today.getFullYear(), 0, 1);
        } else if (preset.type === 'all') {
            // Use empty values to indicate no filtering
            startDateInput.value = '';
            endDateInput.value = '';
            return;
        } else if (preset.days > 0) {
            // Go back X days
            start.setDate(today.getDate() - preset.days);
        }
        
        // Format dates as YYYY-MM-DD for the input fields
        startDateInput.value = formatDate(start);
        endDateInput.value = formatDate(end);
    }
    
    /**
     * Formats a Date object as YYYY-MM-DD string
     * @param {Date} date - The date to format
     * @returns {string} The formatted date string
     */
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
});
