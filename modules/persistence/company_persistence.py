from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import os
from .data_serializer import DataSerializer
from ..core.company import Company


class CompanyPersistence:
    """Handles saving and loading of company data."""

    def __init__(self, serializer: Optional[DataSerializer] = None):
        self.serializer = serializer or DataSerializer()

    def save_company(self, company: Company, filename: Optional[str] = None) -> str:
        """Save a company object to file.

        Args:
            company: Company object to save
            filename: Optional custom filename (defaults to company_id)

        Returns:
            Path to the saved file
        """
        if filename is None:
            filename = f"company_{company.id}"

        # Convert company to dictionary
        company_data = company.to_dict()

        # Add metadata
        company_data['_metadata'] = {
            'saved_at': datetime.now(),
            'version': '1.0',
            'type': 'company'
        }

        return self.serializer.serialize_to_json(company_data, filename)

    def load_company(self, filename: str) -> Company:
        """Load a company object from file.

        Args:
            filename: Filename to load (without extension)

        Returns:
            Company object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data is invalid
        """
        company_data = self.serializer.deserialize_from_json(filename)

        # Validate data
        if not self.serializer.validate_save_data(company_data, 'company'):
            raise ValueError(f"Invalid company data in file: {filename}")

        # Remove metadata before creating company
        company_data.pop('_metadata', None)

        return Company.from_dict(company_data)

    def save_multiple_companies(self, companies: List[Company], filename: str) -> str:
        """Save multiple companies to a single file.

        Args:
            companies: List of Company objects
            filename: Output filename

        Returns:
            Path to the saved file
        """
        companies_data = {
            'companies': [company.to_dict() for company in companies],
            '_metadata': {
                'saved_at': datetime.now(),
                'version': '1.0',
                'type': 'companies',
                'count': len(companies)
            }
        }

        return self.serializer.serialize_to_json(companies_data, filename)

    def load_multiple_companies(self, filename: str) -> List[Company]:
        """Load multiple companies from a single file.

        Args:
            filename: Filename to load

        Returns:
            List of Company objects
        """
        data = self.serializer.deserialize_from_json(filename)

        if 'companies' not in data:
            raise ValueError(f"Invalid companies data in file: {filename}")

        companies = []
        for company_data in data['companies']:
            companies.append(Company.from_dict(company_data))

        return companies

    def save_company_snapshot(self, company: Company, round_number: int) -> str:
        """Save a snapshot of company state at a specific round.

        Args:
            company: Company object
            round_number: Current round number

        Returns:
            Path to the saved snapshot
        """
        filename = f"company_{company.id}_round_{round_number}"
        return self.save_company(company, filename)

    def list_company_saves(self) -> List[Dict[str, Any]]:
        """List all saved company files with metadata.

        Returns:
            List of dictionaries containing file information
        """
        json_files = self.serializer.list_save_files('json')
        company_files = []

        for filename in json_files:
            if filename.startswith('company_'):
                file_info = self.serializer.get_file_info(filename, 'json')
                if file_info:
                    # Try to get basic info from the file
                    try:
                        data = self.serializer.deserialize_from_json(filename)
                        if self.serializer.validate_save_data(data, 'company'):
                            file_info['company_id'] = data.get('id')
                            file_info['company_name'] = data.get('name')
                            file_info['has_metadata'] = '_metadata' in data
                            if file_info['has_metadata']:
                                file_info['saved_at'] = data['_metadata'].get('saved_at')
                    except:
                        pass  # Skip files that can't be read

                    company_files.append(file_info)

        return company_files

    def find_company_snapshots(self, company_id: str) -> List[Dict[str, Any]]:
        """Find all snapshots for a specific company.

        Args:
            company_id: Company ID to search for

        Returns:
            List of snapshot file information
        """
        all_saves = self.list_company_saves()
        snapshots = []

        for save_info in all_saves:
            filename = save_info['filename']
            if f"company_{company_id}_round_" in filename:
                # Extract round number
                try:
                    round_part = filename.split('_round_')[-1]
                    save_info['round_number'] = int(round_part)
                    snapshots.append(save_info)
                except (ValueError, IndexError):
                    continue

        # Sort by round number
        snapshots.sort(key=lambda x: x.get('round_number', 0))

        return snapshots

    def delete_company_save(self, filename: str) -> bool:
        """Delete a company save file.

        Args:
            filename: Filename to delete (without extension)

        Returns:
            True if deleted successfully
        """
        return self.serializer.delete_save_file(filename, 'json')

    def export_company_to_csv(self, company: Company, filename: str) -> str:
        """Export company data to CSV format.

        Args:
            company: Company object to export
            filename: Output filename (without extension)

        Returns:
            Path to the exported CSV file
        """
        import csv

        filepath = Path(self.serializer.base_path) / f"{filename}.csv"

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Category', 'Metric', 'Value'])

            # Write financial data
            writer.writerow(['Financial', 'Revenue', company.financial_data.revenue])
            writer.writerow(['Financial', 'Costs', company.financial_data.costs])
            writer.writerow(['Financial', 'Profit', company.financial_data.profit])
            writer.writerow(['Financial', 'Cash', company.financial_data.cash])
            writer.writerow(['Financial', 'Assets', company.financial_data.assets])
            writer.writerow(['Financial', 'Liabilities', company.financial_data.liabilities])

            # Write operational data
            writer.writerow(['Operational', 'Capacity', company.operations_data.capacity])
            writer.writerow(['Operational', 'Efficiency', company.operations_data.efficiency])
            writer.writerow(['Operational', 'Quality', company.operations_data.quality])
            writer.writerow(['Operational', 'Utilization', company.operations_data.utilization])
            writer.writerow(['Operational', 'Customer Satisfaction', company.operations_data.customer_satisfaction])

            # Write resource data
            writer.writerow(['Resources', 'Employees', company.resource_data.employees])
            writer.writerow(['Resources', 'Equipment Value', company.resource_data.equipment])
            writer.writerow(['Resources', 'Inventory Value', company.resource_data.inventory])

            # Write market data
            writer.writerow(['Market', 'Market Share', company.market_data.market_share])
            writer.writerow(['Market', 'Brand Value', company.market_data.brand_value])
            writer.writerow(['Market', 'Competitive Position', company.market_data.competitive_position])

        return str(filepath)

    def get_company_backup(self, company_id: str) -> Optional[str]:
        """Create a backup of the latest company save.

        Args:
            company_id: Company ID

        Returns:
            Path to backup file, or None if no save exists
        """
        filename = f"company_{company_id}"
        try:
            return self.serializer.create_backup(filename, 'json')
        except FileNotFoundError:
            return None