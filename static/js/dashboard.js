document.addEventListener('DOMContentLoaded', function() {
    // Handle track status form submission
    const statusTrackingForm = document.getElementById('statusTrackingForm');
    if (statusTrackingForm) {
        statusTrackingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const applicationType = document.getElementById('application_type').value;
            const applicationNumber = document.getElementById('application_number').value;
            
            // Show loading state
            const trackingResult = document.getElementById('trackingResult');
            trackingResult.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Fetching status...</p></div>';
            
            // Make AJAX request to check status
            fetch(`/dashboard/status/${applicationType}/${applicationNumber}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    trackingResult.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                } else {
                    // Format the status display
                    let statusBadge = '';
                    if (data.status === 'PENDING') {
                        statusBadge = '<span class="badge bg-warning text-dark">Pending</span>';
                    } else if (data.status === 'APPROVED' || data.status === 'ISSUED') {
                        statusBadge = '<span class="badge bg-success">Approved</span>';
                    } else if (data.status === 'REJECTED') {
                        statusBadge = '<span class="badge bg-danger">Rejected</span>';
                    } else {
                        statusBadge = `<span class="badge bg-info">${data.status}</span>`;
                    }
                    
                    trackingResult.innerHTML = `
                        <div class="alert alert-info">
                            <h6>Application Details</h6>
                            <p><strong>Type:</strong> ${data.application_type}</p>
                            <p><strong>Number:</strong> ${data.application_number}</p>
                            <p><strong>Status:</strong> ${statusBadge}</p>
                            <p><strong>Last Updated:</strong> ${data.last_updated}</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                trackingResult.innerHTML = '<div class="alert alert-danger">Error fetching status. Please try again.</div>';
                console.error('Error:', error);
            });
        });
    }
}); 