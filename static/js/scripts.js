document.addEventListener('DOMContentLoaded', function() {
    // Animate cards on dashboard
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });

    // Dynamic doctor selection based on specialization
    const specializationSelect = document.getElementById('specialization');
    const doctorSelect = document.getElementById('doctor');
    if (specializationSelect && doctorSelect) {
        specializationSelect.addEventListener('change', function() {
            const specialization = this.value;
            // Simulate fetching doctors based on specialization (you can replace with an AJAX call)
            const doctors = {
                'Cardiology': ['D001', 'D002'],
                'Neurology': ['D003'],
                'Orthopedics': ['D004']
            };
            doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
            if (doctors[specialization]) {
                doctors[specialization].forEach(doctor => {
                    const option = document.createElement('option');
                    option.value = doctor;
                    option.textContent = `Doctor ${doctor}`;
                    doctorSelect.appendChild(option);
                });
            }
        });
    }
});