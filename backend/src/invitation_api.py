"""
Invitation Code Management API
Handles invitation-only registration system
"""

import secrets
import string
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from database import db
from core_models import User, InvitationCode

# Create blueprint
invitation_bp = Blueprint('invitation_api', __name__, url_prefix='/api/v1/invitations')

# Auth decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            import jwt
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_obj = User.query.get(current_user_id)
            if not current_user_obj:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_obj, *args, **kwargs)
    return decorated


def generate_invitation_code(length=12):
    """Generate a secure random invitation code"""
    # Use alphanumeric characters (excluding similar-looking ones)
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(chars) for _ in range(length))


@invitation_bp.route('/generate', methods=['POST'])
@token_required
def create_invitation_code(current_user):
    """
    Generate a new invitation code
    Only existing users can create invitations
    """
    try:
        data = request.get_json() or {}

        # Optional parameters
        max_uses = data.get('max_uses', 1)
        expires_in_days = data.get('expires_in_days')
        notes = data.get('notes', '')

        # Validate max_uses
        if max_uses < 1 or max_uses > 100:
            return jsonify({
                'error': 'Invalid max_uses',
                'message': 'max_uses must be between 1 and 100'
            }), 400

        # Generate unique code
        code = generate_invitation_code()
        attempts = 0
        while InvitationCode.query.filter_by(code=code).first() and attempts < 10:
            code = generate_invitation_code()
            attempts += 1

        if attempts >= 10:
            return jsonify({'error': 'Failed to generate unique code'}), 500

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create invitation
        invitation = InvitationCode(
            code=code,
            created_by=current_user.id,
            max_uses=max_uses,
            expires_at=expires_at,
            notes=notes[:255] if notes else None  # Truncate to column limit
        )

        db.session.add(invitation)
        db.session.commit()

        return jsonify({
            'message': 'Invitation code created successfully',
            'invitation': invitation.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating invitation code: {str(e)}")
        return jsonify({
            'error': 'Failed to create invitation code',
            'details': str(e)
        }), 500


@invitation_bp.route('/validate/<code>', methods=['GET'])
def validate_invitation_code(code):
    """
    Validate an invitation code (public endpoint, no auth required)
    Used during registration
    """
    try:
        invitation = InvitationCode.query.filter_by(code=code.upper()).first()

        if not invitation:
            return jsonify({
                'valid': False,
                'message': 'Invalid invitation code'
            }), 404

        is_valid, message = invitation.is_valid()

        return jsonify({
            'valid': is_valid,
            'message': message,
            'invitation': invitation.to_dict() if is_valid else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error validating invitation code: {str(e)}")
        return jsonify({
            'error': 'Failed to validate invitation code'
        }), 500


@invitation_bp.route('/my-codes', methods=['GET'])
@token_required
def get_my_invitation_codes(current_user):
    """
    Get all invitation codes created by the current user
    """
    try:
        invitations = InvitationCode.query.filter_by(
            created_by=current_user.id
        ).order_by(InvitationCode.created_at.desc()).all()

        return jsonify({
            'invitations': [inv.to_dict() for inv in invitations],
            'total': len(invitations),
            'active': len([inv for inv in invitations if inv.is_active])
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting invitation codes: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve invitation codes'
        }), 500


@invitation_bp.route('/<int:invitation_id>/deactivate', methods=['POST'])
@token_required
def deactivate_invitation(current_user, invitation_id):
    """
    Deactivate an invitation code
    Only the creator can deactivate
    """
    try:
        invitation = InvitationCode.query.get_or_404(invitation_id)

        # Check ownership
        if invitation.created_by != current_user.id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only deactivate your own invitation codes'
            }), 403

        invitation.is_active = False
        db.session.commit()

        return jsonify({
            'message': 'Invitation code deactivated successfully',
            'invitation': invitation.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deactivating invitation: {str(e)}")
        return jsonify({
            'error': 'Failed to deactivate invitation code'
        }), 500


@invitation_bp.route('/stats', methods=['GET'])
@token_required
def get_invitation_stats(current_user):
    """
    Get invitation statistics for the current user
    """
    try:
        my_invitations = InvitationCode.query.filter_by(
            created_by=current_user.id
        ).all()

        total_created = len(my_invitations)
        active_codes = len([inv for inv in my_invitations if inv.is_active])
        total_uses = sum(inv.current_uses for inv in my_invitations)
        available_uses = sum(
            inv.max_uses - inv.current_uses
            for inv in my_invitations
            if inv.is_active and (inv.is_valid()[0])
        )

        return jsonify({
            'total_created': total_created,
            'active_codes': active_codes,
            'total_uses': total_uses,
            'available_uses': available_uses
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting invitation stats: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics'
        }), 500
